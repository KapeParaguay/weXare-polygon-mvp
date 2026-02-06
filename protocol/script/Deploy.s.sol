// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/QuestEscrowManager.sol";
import "../src/QuestDisputeManager.sol";

contract Deploy is Script {
    function run() external {
        address admin = vm.envAddress("ADMIN_ADDRESS");
        address usdc = vm.envAddress("USDC_ADDRESS");
        address coop = vm.envAddress("COOP_WALLET_ADDRESS");

        vm.startBroadcast();
        QuestEscrowManager escrow = new QuestEscrowManager(admin, usdc);
        QuestDisputeManager dispute = new QuestDisputeManager(admin);

        escrow.setDisputeManager(address(dispute));
        dispute.setEscrowManager(address(escrow));

        escrow.setCoopWallet(coop);

        escrow.grantRole(escrow.OPERATOR_ROLE(), admin);
        dispute.grantRole(dispute.OPERATOR_ROLE(), admin);
        dispute.grantRole(dispute.OPERATOR_ROLE(), address(escrow));
        escrow.grantRole(escrow.OPERATOR_ROLE(), address(dispute));

        vm.stopBroadcast();

        console2.log("Escrow:", address(escrow));
        console2.log("Dispute:", address(dispute));
    }
}
