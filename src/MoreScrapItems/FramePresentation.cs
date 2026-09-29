using UnityEngine;

namespace Dan.MoreScrapItems;

// Added by the plugin at runtime; the asset bundle contains only native Unity assets.
public sealed class FramePresentation : MonoBehaviour
{
    [SerializeField] private PhysicsProp prop = null!;
    [SerializeField] private MeshFilter filter = null!;
    [SerializeField] private Mesh heldMesh = null!;
    [SerializeField] private Mesh placedMesh = null!;
    [SerializeField] private BoxCollider bodyCollider = null!;
    [SerializeField] private BoxCollider scanCollider = null!;
    [SerializeField] private Bounds heldBounds;
    [SerializeField] private Bounds placedBounds;
    private bool initialized;
    private bool showingHeld;

    public bool ShowingHeld => showingHeld;

    public void Configure(PhysicsProp owner, MeshFilter visual, GameObject held, GameObject placed,
        BoxCollider collider, BoxCollider scanner)
    {
        prop = owner;
        filter = visual;
        heldMesh = held.GetComponentInChildren<MeshFilter>().sharedMesh;
        placedMesh = placed.GetComponentInChildren<MeshFilter>().sharedMesh;
        bodyCollider = collider;
        scanCollider = scanner;
        var heldBox = held.GetComponent<BoxCollider>();
        var placedBox = placed.GetComponent<BoxCollider>();
        heldBounds = new Bounds(heldBox.center, heldBox.size);
        placedBounds = new Bounds(placedBox.center, placedBox.size);
        Refresh();
    }

    private void LateUpdate() => Refresh();

    private void Refresh()
    {
        if (prop == null || filter == null) return;
        // These are the game's replicated grab flags, so each client selects the same mesh.
        bool held = prop.isHeld || prop.isPocketed || prop.isHeldByEnemy;
        if (initialized && held == showingHeld) return;
        initialized = true;
        showingHeld = held;
        filter.sharedMesh = held ? heldMesh : placedMesh;
        var bounds = held ? heldBounds : placedBounds;
        bodyCollider.center = bounds.center;
        bodyCollider.size = bounds.size;
        scanCollider.transform.localPosition = bounds.center;
        scanCollider.size = bounds.size;
    }
}
