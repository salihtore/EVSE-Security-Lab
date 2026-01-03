import { useSignAndExecuteTransaction, useSuiClient } from "@mysten/dapp-kit";
import { Transaction } from "@mysten/sui/transactions";
import { SUI_ADMIN_CONFIG } from "../suiConfig";
import { useCallback } from "react";

export const useAdmin = () => {
    const { mutate: signAndExecuteTransaction } = useSignAndExecuteTransaction();
    const suiClient = useSuiClient();

    const checkIsAdmin = useCallback(async (address) => {
        if (!address) return false;

        const { data } = await suiClient.getOwnedObjects({
            owner: address,
            filter: {
                StructType: `${SUI_ADMIN_CONFIG.PACKAGE_ID}::${SUI_ADMIN_CONFIG.MODULE_NAME}::AdminCap`
            }
        });

        return data && data.length > 0;
    }, [suiClient]);

    const createAdmin = useCallback(async (recipientAddress, onSuccess, onError) => {
        try {
            const tx = new Transaction();

            tx.moveCall({
                target: `${SUI_ADMIN_CONFIG.PACKAGE_ID}::${SUI_ADMIN_CONFIG.MODULE_NAME}::create_admin`,
                arguments: [
                    tx.object(SUI_ADMIN_CONFIG.ADMIN_CAP_ID),
                    tx.pure.address(recipientAddress),
                ],
            });

            signAndExecuteTransaction(
                {
                    transaction: tx,
                },
                {
                    onSuccess: (result) => {
                        console.log("Admin created successfully:", result);
                        if (onSuccess) onSuccess(result);
                    },
                    onError: (error) => {
                        console.error("Failed to create admin:", error);
                        if (onError) onError(error);
                    },
                }
            );
        } catch (error) {
            console.error("Error preparing transaction:", error);
            if (onError) onError(error);
        }
    }, [signAndExecuteTransaction]);

    return { createAdmin, checkIsAdmin };
};
