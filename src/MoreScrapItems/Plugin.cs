using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Collections;
using System.Reflection;
using BepInEx;
using BepInEx.Configuration;
using LethalLib.Modules;
using UnityEngine;

namespace Dan.MoreScrapItems;

[BepInPlugin(Guid, Name, Version)]
[BepInDependency("evaisa.lethallib", BepInDependency.DependencyFlags.HardDependency)]
public sealed class Plugin : BaseUnityPlugin
{
    public const string Guid = "dansi.more-scrap-items";
    public const string Name = "More Scrap Items";
    public const string Version = "0.1.0";
    private AssetBundle? assets;
    private readonly List<Item> registered = new();
    private ConfigEntry<bool>? testSpawn;
    private ConfigEntry<bool>? testHolding;
    private readonly Dictionary<string, (ConfigEntry<Vector3> position, ConfigEntry<Vector3> rotation)> poses = new();
    private bool testSpawnDone;

    private void Awake()
    {
        testSpawn = Config.Bind("Development", "SpawnInShipForTesting", false, "Host only: spawn one of each item near the player once per game launch, for local testing.");
        testHolding = Config.Bind("Development", "RunHoldingTest", false, "Local development only: use the game's normal grab and discard routines to inspect both items. Requires SpawnInShipForTesting.");
        var mugRarity = Config.Bind("Spawn", "QuotaMugRarity", 25,
            new ConfigDescription("Relative spawn weight on all moons. Set 0 to disable.", new AcceptableValueRange<int>(0, 1000)));
        var frameRarity = Config.Bind("Spawn", "MoonFrameRarity", 18,
            new ConfigDescription("Relative spawn weight on all moons. Set 0 to disable.", new AcceptableValueRange<int>(0, 1000)));
        var bundlePath = Path.Combine(Path.GetDirectoryName(Info.Location)!, "morescrapassets");
        assets = AssetBundle.LoadFromFile(bundlePath);
        if (assets == null) throw new InvalidOperationException("Cannot load More Scrap Items asset bundle: " + bundlePath);
        Register("QuotaMug", "Quota mug", 71001, 50, 110, 1.03f, mugRarity.Value);
        Register("MoonFrame", "Moon frame", 71002, 90, 180, 1.06f, frameRarity.Value);
        Logger.LogInfo("More Scrap Items 0.1.0: Quota mug and Moon frame registered.");
        if (testSpawn.Value) On.StartOfRound.Start += StartRoundForTesting;
    }

    private void Register(string id, string title, int itemId, int min, int max, float weight, int rarity)
    {
        var model = assets!.LoadAsset<GameObject>($"Assets/MoreScrapItems/Prefabs/{id}.prefab");
        if (model == null) throw new InvalidOperationException("Missing model: " + id);
        var prefab = NetworkPrefabs.CreateNetworkPrefab(Guid + "." + id);
        DontDestroyOnLoad(prefab.transform.root.gameObject);
        prefab.tag = "PhysicsProp"; prefab.layer = LayerMask.NameToLayer("Props");
        var visual = Instantiate(model, prefab.transform);
        visual.name = "Model";
        var renderers = visual.GetComponentsInChildren<MeshRenderer>(true);
        foreach (var renderer in renderers) renderer.gameObject.layer = prefab.layer;
        var modelCollider = visual.GetComponent<BoxCollider>();
        var collider = prefab.AddComponent<BoxCollider>();
        collider.center = modelCollider.center; collider.size = modelCollider.size;
        DestroyImmediate(modelCollider);
        var body = prefab.AddComponent<Rigidbody>(); body.isKinematic = true; body.useGravity = false;
        var audio = prefab.AddComponent<AudioSource>(); audio.playOnAwake = false;
        audio.spatialBlend = 1; audio.volume = .35f; audio.minDistance = 1; audio.maxDistance = 12;
        var item = ScriptableObject.CreateInstance<Item>();
        item.name = id; item.itemName = title; item.itemId = itemId;
        item.isScrap = true; item.minValue = min; item.maxValue = max; item.weight = weight;
        item.requiresBattery = false; item.canBeGrabbedBeforeGameStart = true;
        item.isConductiveMetal = id == "QuotaMug";
        item.spawnPositionTypes = new List<ItemGroup>(); item.toolTips = Array.Empty<string>();
        item.meshVariants = Array.Empty<Mesh>(); item.materialVariants = Array.Empty<Material>();
        item.clinkAudios = Array.Empty<AudioClip>();
        var sound = MakeSound(id, id == "QuotaMug" ? 1700f : 650f);
        item.grabSFX = sound; item.dropSFX = sound; item.pocketSFX = sound;
        item.restingRotation = Vector3.zero;
        item.verticalOffset = collider.size.y / 2;
        item.positionOffset = id == "QuotaMug" ? new Vector3(.015f,.22f,-.02f) : new Vector3(.18f,.24f,0);
        // The game's hand anchor has a quarter-turn roll: compensate so each model stays upright.
        item.rotationOffset = new Vector3(0,180,90);
        var position = Config.Bind("Holding", id + "Position", item.positionOffset, "Position relative to the game's hand anchor, in metres.");
        var rotation = Config.Bind("Holding", id + "Rotation", item.rotationOffset, "Rotation relative to the game's hand anchor, in degrees.");
        poses[id] = (position, rotation);
        item.positionOffset = position.Value; item.rotationOffset = rotation.Value;
        item.itemIcon = assets.LoadAsset<Sprite>($"Assets/MoreScrapItems/Models/{id}Icon.png");
        item.spawnPrefab = prefab;
        var prop = prefab.AddComponent<PhysicsProp>();
        prop.itemProperties = item; prop.grabbable = true; prop.grabbableToEnemies = true;
        prop.propBody = body; prop.propColliders = new Collider[] { collider }; prop.mainObjectRenderer = renderers[0];
        var scanner = new GameObject("ScanNode"); scanner.transform.SetParent(prefab.transform, false);
        scanner.layer = LayerMask.NameToLayer("ScanNode"); scanner.transform.localPosition = collider.center;
        var scanCollider = scanner.AddComponent<BoxCollider>(); scanCollider.size = collider.size;
        var scan = scanner.AddComponent<ScanNodeProperties>();
        scan.headerText = title; scan.subText = "Value: $0"; scan.nodeType = 2;
        scan.maxRange = 13; scan.minRange = 1; scan.requiresLineOfSight = true;
        if (id == "MoonFrame")
        {
            var placed = assets.LoadAsset<GameObject>("Assets/MoreScrapItems/Prefabs/MoonFramePlaced.prefab");
            if (placed == null) throw new InvalidOperationException("Missing placed frame model; update DLL and asset bundle together.");
            var placedBox = placed.GetComponent<BoxCollider>();
            // The game raises a discarded prop by about 4 cm after applying verticalOffset.
            item.verticalOffset = placedBox.size.y / 2 - placedBox.center.y - .04f;
            prefab.AddComponent<FramePresentation>().Configure(prop, visual.GetComponentInChildren<MeshFilter>(),
                model, placed, collider, scanCollider);
        }
        Utilities.FixMixerGroups(prefab);
        Items.RegisterScrap(item, rarity, Levels.LevelTypes.All);
        registered.Add(item);
        Logger.LogInfo($"Registered {item.itemName}; value {item.minValue}-{item.maxValue}; rarity {rarity}.");
    }

    private void StartRoundForTesting(On.StartOfRound.orig_Start original, StartOfRound round)
    {
        original(round);
        if (!testSpawnDone) round.StartCoroutine(SpawnForTesting());
    }

    private IEnumerator SpawnForTesting()
    {
        yield return new WaitForSeconds(3);
        var playerController = GameNetworkManager.Instance?.localPlayerController;
        if (Unity.Netcode.NetworkManager.Singleton == null || !Unity.Netcode.NetworkManager.Singleton.IsHost || playerController == null) yield break;
        testSpawnDone = true;
        var spawned = new List<PhysicsProp>();
        for (int index = 0; index < registered.Count; index++)
        {
            var player = playerController.transform;
            var instance = Instantiate(registered[index].spawnPrefab, player.position + player.forward * 1.5f + player.right * (index * .6f - .3f) + Vector3.up, Quaternion.identity);
            instance.GetComponent<Unity.Netcode.NetworkObject>().Spawn();
            instance.GetComponent<PhysicsProp>().SetScrapValue((registered[index].minValue + registered[index].maxValue) / 2);
            spawned.Add(instance.GetComponent<PhysicsProp>());
            Logger.LogInfo("TEST_SPAWN_COMPLETE " + registered[index].itemName);
        }
        if (!testHolding!.Value) yield break;
        yield return new WaitForSeconds(2);
        var beginGrab = playerController.GetType().GetMethod("BeginGrabObject", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)!;
        foreach (var prop in spawned)
        {
            // Exercise the actual raycast, network RPC, inventory and grab animation.
            var camera = playerController.gameplayCamera.transform;
            prop.transform.position = camera.position + camera.forward * 1.3f;
            prop.fallTime = 1; prop.hasHitGround = true;
            Physics.SyncTransforms();
            beginGrab.Invoke(playerController, null);
            yield return new WaitForSeconds(2);
            bool valid = playerController.currentlyHeldObjectServer == prop && prop.isHeld && prop.parentObject == playerController.localItemHolder;
            Logger.LogInfo($"HOLD_TEST {prop.itemProperties.itemName}: held={valid}; hand={prop.parentObject?.eulerAngles}; model={prop.transform.eulerAngles}");
            LogFrameState(prop, "held");
            if (!valid) { Logger.LogError("Normal grab failed in holding test."); yield break; }
            for (int second = 0; second < 45; second++)
            {
                Config.Reload();
                var pose = poses[prop.itemProperties.name];
                prop.itemProperties.positionOffset = pose.position.Value;
                prop.itemProperties.rotationOffset = pose.rotation.Value;
                yield return new WaitForSeconds(1);
            }
            playerController.DiscardHeldObject();
            yield return new WaitForSeconds(2);
            Logger.LogInfo($"DROP_TEST {prop.itemProperties.itemName}: released={!prop.isHeld && prop.parentObject == null}");
            LogFrameState(prop, "placed");
            if (prop.GetComponent<FramePresentation>() != null)
            {
                yield return new WaitForSeconds(8);
                prop.transform.position = camera.position + camera.forward * 1.3f;
                prop.fallTime = 1; prop.hasHitGround = true;
                Physics.SyncTransforms();
                beginGrab.Invoke(playerController, null);
                yield return new WaitForSeconds(2);
                Logger.LogInfo($"REGRAB_TEST Moon frame: held={prop.isHeld && playerController.currentlyHeldObjectServer == prop}");
                LogFrameState(prop, "held");
                yield return new WaitForSeconds(8);
                playerController.DiscardHeldObject();
                yield return new WaitForSeconds(2);
                LogFrameState(prop, "placed");
            }
        }
    }

    private void LogFrameState(PhysicsProp prop, string expected)
    {
        var frame = prop.GetComponent<FramePresentation>();
        if (frame == null) return;
        var mesh = prop.GetComponentInChildren<MeshFilter>().sharedMesh;
        bool valid = frame.ShowingHeld == (expected == "held");
        Logger.LogInfo($"FRAME_STATE expected={expected}; valid={valid}; mesh={mesh.name}; floorOffset={prop.itemProperties.verticalOffset:F4}; localBounds={prop.GetComponent<BoxCollider>().size}");
        if (!valid) Logger.LogError("Frame presentation did not match the grab state.");
        if (expected == "placed")
        {
            var bounds = prop.mainObjectRenderer.bounds;
            if (Physics.Raycast(bounds.center + Vector3.up * .5f, Vector3.down, out var hit, 2,
                LayerMask.GetMask("Room", "Colliders"), QueryTriggerInteraction.Ignore))
                Logger.LogInfo($"FRAME_FLOOR gap={bounds.min.y - hit.point.y:F4}; rendererCount={prop.GetComponentsInChildren<MeshRenderer>().Length}");
        }
    }

    private static AudioClip MakeSound(string name, float frequency)
    {
        const int rate = 22050;
        var samples = new float[rate / 10];
        for (int i = 0; i < samples.Length; i++)
        {
            float time = i / (float)rate;
            samples[i] = .2f * (float)(Math.Sin(2 * Math.PI * frequency * time) * Math.Exp(-time * 65));
        }
        var clip = AudioClip.Create(name + "Clink", samples.Length, 1, rate, false);
        clip.SetData(samples, 0);
        return clip;
    }
}
