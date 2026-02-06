// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/QuestEscrowManager.sol";
import "../src/QuestDisputeManager.sol";

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

contract ForkUSDCTest is Test {
    address constant USDC = 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174;
    QuestEscrowManager escrow;
    QuestDisputeManager dispute;

    bool forkEnabled;

    address admin = address(0x100);
    address payer = address(0x200);
    address payee = address(0x300);
    address judge1 = address(0x400);
    address judge2 = address(0x500);
    address judge3 = address(0x600);

    function setUp() public {
        forkEnabled = vm.envOr("FORK", false);
        if (!forkEnabled) {
            return;
        }
        require(address(USDC).code.length > 0, "USDC_NOT_AVAILABLE");

        escrow = new QuestEscrowManager(admin, USDC);
        dispute = new QuestDisputeManager(admin);

        vm.startPrank(admin);
        escrow.grantRole(escrow.OPERATOR_ROLE(), admin);
        escrow.grantRole(escrow.OPERATOR_ROLE(), address(dispute));
        dispute.grantRole(dispute.OPERATOR_ROLE(), admin);
        dispute.grantRole(dispute.OPERATOR_ROLE(), address(escrow));
        escrow.setDisputeManager(address(dispute));
        dispute.setEscrowManager(address(escrow));
        vm.stopPrank();

        // Use cheatcode to set USDC balance on fork
        deal(USDC, payer, 1_000_000e6);

        vm.startPrank(payer);
        IERC20Like(USDC).approve(address(escrow), 1_000_000e6);
        vm.stopPrank();
    }

    function testForkEscrowAndDispute() public {
        if (!forkEnabled) {
            return;
        }
        vm.startPrank(admin);
        escrow.fundQuest(1, 0, payer, payee, 100e6, keccak256("scope"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(1, 11, keccak256("c"), keccak256("w"));
        dispute.assignJudges(11, judge1, judge2, judge3);
        vm.stopPrank();

        vm.prank(judge1);
        dispute.submitVote(11, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c1"));
        vm.prank(judge2);
        dispute.submitVote(11, QuestDisputeManager.VoteType.SUCCESS, 0, keccak256("c2"));

        vm.startPrank(admin);
        dispute.finalizeAndExecute(11);
        vm.stopPrank();

        assertEq(IERC20Like(USDC).balanceOf(payee), 100e6);
    }
}
