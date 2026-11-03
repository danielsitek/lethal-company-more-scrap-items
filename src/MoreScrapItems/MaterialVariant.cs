using UnityEngine;

namespace Dan.MoreScrapItems;

// Added by the plugin at runtime; picks one material per spawned item.
// The choice comes from the replicated NetworkObjectId, so every client shows the same
// variant without an RPC. Reloading a save assigns new IDs and may change the variant.
public sealed class MaterialVariant : MonoBehaviour
{
    [SerializeField] private PhysicsProp prop = null!;
    [SerializeField] private MeshRenderer target = null!;
    [SerializeField] private Material[] variants = null!;

    public void Configure(PhysicsProp owner, MeshRenderer renderer, Material[] materials)
    {
        prop = owner;
        target = renderer;
        variants = materials;
    }

    private void Update()
    {
        if (!prop.IsSpawned) return;
        target.sharedMaterial = variants[Pick(prop.NetworkObjectId, variants.Length)];
        enabled = false;
    }

    // NetworkObjectIds are mostly sequential; mix the bits so nearby items do not cycle in order.
    private static int Pick(ulong id, int count)
    {
        id ^= id >> 33;
        id *= 0xff51afd7ed558ccdUL;
        id ^= id >> 33;
        return (int)(id % (ulong)count);
    }
}
