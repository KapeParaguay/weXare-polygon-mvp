// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/QuestEscrowManager.sol";
import "../src/QuestDisputeManager.sol";

contract MockUSDC is IERC20 {
    string public name = "USDC";
    string public symbol = "USDC";
    uint8 public decimals = 6;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(allowance[from][msg.sender] >= amount, "NO_ALLOWANCE");
        require(balanceOf[from] >= amount, "NO_BALANCE");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "NO_BALANCE");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

contract QuestProtocolTest is Test {
    QuestEscrowManager escrow;
    QuestDisputeManager dispute;
    MockUSDC usdc;

    address admin = address(0x1);
    address operator = address(0x2);
    address payer = address(0x3);
    address payee = address(0x4);
    address judge1 = address(0x5);
    address judge2 = address(0x6);
    address judge3 = address(0x7);

    function setUp() public {
        usdc = new MockUSDC();
        escrow = new QuestEscrowManager(admin, address(usdc));
        dispute = new QuestDisputeManager(admin);

        vm.startPrank(admin);
        escrow.grantRole(escrow.OPERATOR_ROLE(), operator);
        escrow.grantRole(escrow.OPERATOR_ROLE(), address(dispute));
        dispute.grantRole(dispute.OPERATOR_ROLE(), operator);
        dispute.grantRole(dispute.OPERATOR_ROLE(), address(escrow));
        escrow.setDisputeManager(address(dispute));
        dispute.setEscrowManager(address(escrow));
        vm.stopPrank();

        usdc.mint(payer, 1_000_000e6);
        vm.prank(payer);
        usdc.approve(address(escrow), 1_000_000e6);
    }

    function testReleaseFlow() public {
        vm.startPrank(operator);
        escrow.fundQuest(1, 0, payer, payee, 100e6, keccak256("scope"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.submitQuest(1, keccak256("evidence"));
        escrow.approveQuest(1);
        escrow.executeQuest(1, QuestEscrowManager.DecisionType.SUCCESS, 0);
        vm.stopPrank();
        assertEq(usdc.balanceOf(payee), 100e6);
    }

    function testDisputeMajorityRelease() public {
        vm.startPrank(operator);
        escrow.fundQuest(2, 0, payer, payee, 100e6, keccak256("scope2"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(2, 11, keccak256("c"), keccak256("w"));
        dispute.assignJudges(11, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(judge1);
        dispute.submitVote(11, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c1"));
        vm.prank(judge2);
        dispute.submitVote(11, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c2"));

        vm.startPrank(operator);
        dispute.finalizeAndExecute(11);
        vm.stopPrank();

        assertEq(usdc.balanceOf(payee), 100e6);
    }

    function testRefundFlow() public {
        vm.startPrank(operator);
        escrow.fundQuest(3, 0, payer, payee, 100e6, keccak256("scope3"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(3, 12, keccak256("c"), keccak256("w"));
        dispute.assignJudges(12, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(judge1);
        dispute.submitVote(12, QuestDisputeManager.VoteType.FAIL, 0, keccak256("c1"));
        vm.prank(judge2);
        dispute.submitVote(12, QuestDisputeManager.VoteType.FAIL, 0, keccak256("c2"));

        vm.startPrank(operator);
        dispute.finalizeAndExecute(12);
        vm.stopPrank();

        assertEq(usdc.balanceOf(payer), 1_000_000e6);
    }

    function testSplitFlowBucketed() public {
        vm.startPrank(operator);
        escrow.fundQuest(4, 0, payer, payee, 100e6, keccak256("scope4"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(4, 13, keccak256("c"), keccak256("w"));
        dispute.assignJudges(13, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(judge1);
        dispute.submitVote(13, QuestDisputeManager.VoteType.SPLIT, 2500, keccak256("c1"));
        vm.prank(judge2);
        dispute.submitVote(13, QuestDisputeManager.VoteType.SPLIT, 2600, keccak256("c2"));

        vm.startPrank(operator);
        dispute.finalizeAndExecute(13);
        vm.stopPrank();

        assertEq(usdc.balanceOf(payee), 25e6);
        assertEq(usdc.balanceOf(payer), 1_000_000e6 - 100e6 + 75e6);
    }

    function testNonJudgeCannotVote() public {
        vm.startPrank(operator);
        escrow.fundQuest(14, 0, payer, payee, 100e6, keccak256("scope14"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(14, 14, keccak256("c"), keccak256("w"));
        dispute.assignJudges(14, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(address(0x99));
        vm.expectRevert("NOT_JUDGE");
        dispute.submitVote(14, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c"));
    }

    function testDoubleExecuteBlocked() public {
        vm.startPrank(operator);
        escrow.fundQuest(5, 0, payer, payee, 100e6, keccak256("scope5"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.approveQuest(5);
        escrow.executeQuest(5, QuestEscrowManager.DecisionType.SUCCESS, 0);
        vm.expectRevert("ALREADY_EXECUTED");
        escrow.executeQuest(5, QuestEscrowManager.DecisionType.SUCCESS, 0);
        vm.stopPrank();
    }

    function testScopeHashImmutable() public {
        vm.startPrank(operator);
        escrow.fundQuest(6, 0, payer, payee, 100e6, keccak256("scope6"), QuestEscrowManager.ExecutionType.HUMAN);
        vm.expectRevert("INVALID_STATUS");
        escrow.fundQuest(6, 0, payer, payee, 100e6, keccak256("scope6b"), QuestEscrowManager.ExecutionType.HUMAN);
        vm.stopPrank();
    }

    function testInvalidStateTransitions() public {
        vm.startPrank(operator);
        vm.expectRevert("INVALID_STATUS");
        escrow.approveQuest(99);
        vm.stopPrank();
    }

    function testNoDoubleVote() public {
        vm.startPrank(operator);
        escrow.fundQuest(7, 0, payer, payee, 100e6, keccak256("scope7"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(7, 17, keccak256("c"), keccak256("w"));
        dispute.assignJudges(17, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(judge1);
        dispute.submitVote(17, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c1"));
        vm.prank(judge1);
        vm.expectRevert("ALREADY_VOTED");
        dispute.submitVote(17, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c2"));
    }

    function testQuestTreeIsolation() public {
        vm.startPrank(operator);
        escrow.fundQuest(100, 0, payer, payee, 50e6, keccak256("parent"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.fundQuest(101, 100, payer, payee, 25e6, keccak256("child"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.approveQuest(101);
        escrow.executeQuest(101, QuestEscrowManager.DecisionType.SUCCESS, 0);
        vm.stopPrank();
        // Parent quest should remain FUNDED
        (,,,,,, QuestEscrowManager.QuestStatus status,,,,,,) = escrow.quests(100);
        assertEq(uint8(status), uint8(QuestEscrowManager.QuestStatus.FUNDED));
    }

    function testQuestChildDifferentPayee() public {
        address payee2 = address(0x9);
        vm.startPrank(operator);
        escrow.fundQuest(200, 0, payer, payee, 50e6, keccak256("parent2"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.fundQuest(201, 200, payer, payee2, 25e6, keccak256("child2"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.approveQuest(201);
        escrow.executeQuest(201, QuestEscrowManager.DecisionType.SUCCESS, 0);
        vm.stopPrank();
        assertEq(usdc.balanceOf(payee2), 25e6);
    }

    function testDisputeChildDoesNotAffectParent() public {
        vm.startPrank(operator);
        escrow.fundQuest(300, 0, payer, payee, 50e6, keccak256("parent3"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.fundQuest(301, 300, payer, payee, 25e6, keccak256("child3"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(301, 5301, keccak256("c"), keccak256("w"));
        dispute.assignJudges(5301, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(judge1);
        dispute.submitVote(5301, QuestDisputeManager.VoteType.FAIL, 0, keccak256("c1"));
        vm.prank(judge2);
        dispute.submitVote(5301, QuestDisputeManager.VoteType.FAIL, 0, keccak256("c2"));

        vm.startPrank(operator);
        dispute.finalizeAndExecute(5301);
        vm.stopPrank();

        (,,,,,, QuestEscrowManager.QuestStatus parentStatus,,,,,,) = escrow.quests(300);
        assertEq(uint8(parentStatus), uint8(QuestEscrowManager.QuestStatus.FUNDED));
    }

    function testRoleGuarded() public {
        vm.expectRevert();
        escrow.fundQuest(8, 0, payer, payee, 100e6, keccak256("scope8"), QuestEscrowManager.ExecutionType.HUMAN);
    }

    function testCancelPreFunding() public {
        vm.startPrank(operator);
        escrow.cancelQuest(9);
        vm.expectRevert("INVALID_STATUS");
        escrow.fundQuest(9, 0, payer, payee, 100e6, keccak256("scope9"), QuestEscrowManager.ExecutionType.HUMAN);
        vm.stopPrank();
    }

    function testPauseBlocksFundingAndExecution() public {
        vm.startPrank(admin);
        escrow.pause();
        vm.stopPrank();

        vm.startPrank(operator);
        vm.expectRevert();
        escrow.fundQuest(10, 0, payer, payee, 100e6, keccak256("scope10"), QuestEscrowManager.ExecutionType.HUMAN);
        vm.stopPrank();

        vm.startPrank(admin);
        escrow.unpause();
        vm.stopPrank();

        vm.startPrank(operator);
        escrow.fundQuest(10, 0, payer, payee, 100e6, keccak256("scope10"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.approveQuest(10);
        vm.stopPrank();

        vm.startPrank(admin);
        escrow.pause();
        vm.stopPrank();

        vm.startPrank(operator);
        vm.expectRevert();
        escrow.executeQuest(10, QuestEscrowManager.DecisionType.SUCCESS, 0);
        vm.stopPrank();
    }
}
