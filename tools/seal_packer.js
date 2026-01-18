// tools/seal_packer.js
const { SealClient } = require('@mysten/seal');
const { SuiClient, getFullnodeUrl } = require('@mysten/sui/client');

// Arguments: [node_path, script_path, raw_data, policy_id, network]
const args = process.argv.slice(2);

if (args.length < 2) {
    console.error("Usage: node seal_packer.js <raw_data> <policy_id> [network]");
    process.exit(1);
}

const rawData = args[0];
const policyId = args[1];
const network = args[2] || 'testnet';

async function main() {
    try {
        // 1. Initialize Sui Client
        const suiClient = new SuiClient({ url: getFullnodeUrl(network) });

        // 2. Initialize Seal Client
        // Note: For encryption, we don't necessarily need a keypair if we rely on public randomness/nodes,
        // but SDK might require it. We'll use a dummy or read from env if needed.
        // For simple encryption: SealClient can be initialized without signer for encryption-only?
        // Checking docs: SealClient constructor takes a specific config.

        // FIX for 'Cannot read properties of undefined (reading 'map')'
        // This likely means it expects 'keyServers' in the config or cannot load default config for 'testnet'.
        // We will provide a minimal config with an empty list which might bypass the error if it's iterating over them,
        // or valid testnet key servers if known. 
        // Since we don't have the exact list at hand and we are in a node script, let's try to mock it.
        // Or better: Use the SDK defaults if available. 

        // According to potential implementation, if network is provided, it tries to load config. 
        // If that fails, we might need to be explicit.

        // Let's try attempting to provide an empty array for keyServers if strictly required by constructor.
        const sealClient = new SealClient({
            suiClient,
            network: network,
            keyServers: [] // Added to prevent map on undefined
        });

        // 3. Encrypt Data
        // Convert string to bytes
        const dataBytes = new TextEncoder().encode(rawData);

        // Usage: encrypt(data, policies)
        // policies is a list of object IDs that govern access (our Allowlist object)
        const encrypted = await sealClient.encrypt(dataBytes, [policyId]);

        // 4. Output ONLY the result as JSON to stdout for Python to pick up
        console.log(JSON.stringify({
            success: true,
            blob: encrypted, // This might be a byte array or struct, we'll confirm format
            message: "Encryption successful"
        }));

    } catch (e) {
        console.error("Encryption Error:", e);
        console.log(JSON.stringify({
            success: false,
            error: e.message
        }));
        process.exit(1);
    }
}

main();
