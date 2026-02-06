// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/QuestEscrowManager.sol";
import "../src/QuestDisputeManager.sol";

contract SmokeTest is Script {
    function run() external {
        address escrowAddr = vm.envAddress("ESCROW_ADDRESS");
        address disputeAddr = vm.envAddress("DISPUTE_ADDRESS");
        address payer = vm.envAddress("PAYER_ADDRESS");
        address payee = vm.envAddress("PAYEE_ADDRESS");

        QuestEscrowManager escrow = QuestEscrowManager(escrowAddr);
        QuestDisputeManager dispute = QuestDisputeManager(disputeAddr);

        vm.startBroadcast();

        uint256 questId = 1001;
        uint256 disputeId = 5001;

        escrow.fundQuest(questId, 0, payer, payee, 1e6, keccak256("scope"), QuestEscrowManager.ExecutionType.HUMAN);
        escrow.openDispute(questId, disputeId, keccak256("c"), keccak256("w"));
        dispute.assignJudges(disputeId, vm.envAddress("JUDGE1"), vm.envAddress("JUDGE2"), vm.envAddress("JUDGE3"));

        vm.stopBroadcast();
    }
}
