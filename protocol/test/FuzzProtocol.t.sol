// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/QuestEscrowManager.sol";

contract MockUSDCFuzz is IERC20 {
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    function mint(address to, uint256 amount) external { balanceOf[to] += amount; totalSupply += amount; }
    function approve(address spender, uint256 amount) external returns (bool) { allowance[msg.sender][spender] = amount; return true; }
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        if (allowance[from][msg.sender] < amount) revert();
        if (balanceOf[from] < amount) revert();
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
    function transfer(address to, uint256 amount) external returns (bool) {
        if (balanceOf[msg.sender] < amount) revert();
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

contract FuzzProtocol is Test {
    QuestEscrowManager escrow;
    MockUSDCFuzz usdc;
    address admin = address(0x1);
    address operator = address(0x2);
    address payer = address(0x3);
    address payee = address(0x4);

    function setUp() public {
        usdc = new MockUSDCFuzz();
        escrow = new QuestEscrowManager(admin, address(usdc));
        vm.startPrank(admin);
        escrow.grantRole(escrow.OPERATOR_ROLE(), operator);
        vm.stopPrank();
        usdc.mint(payer, 1_000_000e6);
        vm.prank(payer);
        usdc.approve(address(escrow), 1_000_000e6);
    }

    function testFuzzConservation(uint96 amount, uint16 splitBps) public {
        vm.assume(amount > 0 && amount < 1_000_000e6);
        vm.assume(splitBps <= 10000);

        uint256 beforePayer = usdc.balanceOf(payer);
        uint256 beforePayee = usdc.balanceOf(payee);

        vm.startPrank(operator);
        escrow.fundQuest(100, 0, payer, payee, amount, keccak256("scope"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.approveQuest(100);
        escrow.executeQuest(100, QuestEscrowManager.DecisionType.SPLIT, splitBps);
        vm.stopPrank();

        uint256 afterPayer = usdc.balanceOf(payer);
        uint256 afterPayee = usdc.balanceOf(payee);

        assertEq(beforePayer + beforePayee, afterPayer + afterPayee);
    }
}
