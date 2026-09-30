using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

[InitializeOnLoad]
public static class MoreScrapAssetBuilder
{
    const string Root = "Assets/MoreScrapItems";

    static MoreScrapAssetBuilder()
    {
        EditorApplication.delayCall += () => {
            if (!File.Exists("build-more-scrap.request")) return;
            File.Delete("build-more-scrap.request");
            Build();
        };
    }

    [MenuItem("Tools/More Scrap Items/Build models and scrap bundle")]
    public static void Build()
    {
        try
        {
            Directory.CreateDirectory(Root + "/Materials");
            Directory.CreateDirectory(Root + "/Prefabs");
            AssetDatabase.Refresh();
            MakeModel("QuotaMug", 1.6f);
            MakeModel("MoonFrame", 1.4f);
            MakeModel("MoonFramePlaced", 1.4f, "MoonFrame");
            MakeModel("Ringhoffer240", 1.0f);
            AssetDatabase.SaveAssets();
            var paths = new[] {
                Root + "/Prefabs/QuotaMug.prefab", Root + "/Prefabs/MoonFrame.prefab",
                Root + "/Prefabs/MoonFramePlaced.prefab",
                Root + "/Prefabs/Ringhoffer240.prefab",
                Root + "/Models/QuotaMugIcon.png", Root + "/Models/MoonFrameIcon.png",
                Root + "/Models/Ringhoffer240Icon.png", Root + "/Audio/Ringhoffer240Bell.wav"
            };
            var report = new List<string>();
            foreach (var path in paths.Take(4))
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var meshes = prefab.GetComponentsInChildren<MeshFilter>();
                var renderers = prefab.GetComponentsInChildren<MeshRenderer>();
                var triangles = meshes.Sum(m => m.sharedMesh.triangles.Length / 3);
                if (triangles == 0 || renderers.Length != 1 || renderers[0].sharedMaterials.Length != 1)
                    throw new Exception(prefab.name + ": expected a nonempty mesh with one renderer and one material.");
                if (meshes.Any(m => m.sharedMesh.uv.Length != m.sharedMesh.vertexCount))
                    throw new Exception(prefab.name + ": missing texture UVs.");
                var texture = renderers[0].sharedMaterial.GetTexture("_BaseColorMap") as Texture2D;
                if (texture == null || texture.width != 512 || texture.height != 512 || texture.mipmapCount <= 1)
                    throw new Exception(prefab.name + ": expected a 512x512 atlas with mipmaps.");
                var bounds = renderers[0].bounds;
                if (prefab.name == "Ringhoffer240" &&
                    (bounds.size.x < .535f || bounds.size.x > .545f))
                    throw new Exception($"Ringhoffer240 must be 0.540 m long in Unity; got {bounds.size.x:F4} m.");
                report.Add($"{prefab.name} triangles={triangles} renderers={renderers.Length} materials=1 texture={texture.width}x{texture.height} format={texture.format} mipmaps={texture.mipmapCount} bounds={bounds.size}");
            }
            Directory.CreateDirectory("Builds/MoreScrapItems");
            var result = BuildPipeline.BuildAssetBundles("Builds/MoreScrapItems",
                new[] { new AssetBundleBuild { assetBundleName = "morescrapassets", assetNames = paths } },
                BuildAssetBundleOptions.ChunkBasedCompression | BuildAssetBundleOptions.StrictMode |
                BuildAssetBundleOptions.ForceRebuildAssetBundle, BuildTarget.StandaloneWindows64);
            if (result == null) throw new Exception("Bundle build failed.");
            File.WriteAllLines("Builds/MoreScrapItems/asset-validation.txt", report);
            if (File.Exists("more-scrap-build-error.txt")) File.Delete("more-scrap-build-error.txt");
            Debug.Log("MORE_SCRAP_BUILD_COMPLETE\n" + string.Join("\n", report));
        }
        catch (Exception e)
        {
            File.WriteAllText("more-scrap-build-error.txt", e.ToString());
            Debug.LogException(e);
            if (Application.isBatchMode) throw;
        }
    }

    static void MakeModel(string id, float scale, string textureId = null)
    {
        textureId = textureId ?? id;
        var modelPath = Root + "/Models/" + id + ".fbx";
        var modelImporter = (ModelImporter)AssetImporter.GetAtPath(modelPath);
        modelImporter.importAnimation = false;
        modelImporter.importCameras = false;
        modelImporter.importLights = false;
        modelImporter.importBlendShapes = false;
        modelImporter.globalScale = id == "Ringhoffer240" ? 100f : 1f;
        modelImporter.isReadable = false;
        modelImporter.SaveAndReimport();
        var texturePath = Root + "/Textures/" + textureId + "BaseColor.png";
        var textureImporter = (TextureImporter)AssetImporter.GetAtPath(texturePath);
        if (textureImporter == null) throw new Exception("Missing atlas: " + texturePath);
        textureImporter.textureType = TextureImporterType.Default;
        textureImporter.sRGBTexture = true;
        textureImporter.alphaSource = TextureImporterAlphaSource.None;
        textureImporter.mipmapEnabled = true;
        textureImporter.isReadable = false;
        textureImporter.maxTextureSize = 512;
        textureImporter.wrapMode = TextureWrapMode.Clamp;
        textureImporter.filterMode = FilterMode.Bilinear;
        textureImporter.anisoLevel = 1;
        textureImporter.textureCompression = TextureImporterCompression.CompressedHQ;
        var standalone = textureImporter.GetPlatformTextureSettings("Standalone");
        standalone.overridden = true;
        standalone.maxTextureSize = 512;
        standalone.format = TextureImporterFormat.BC7;
        textureImporter.SetPlatformTextureSettings(standalone);
        textureImporter.SaveAndReimport();

        var root = new GameObject(id);
        try
        {
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            if (model == null) throw new Exception("Missing model: " + modelPath);
            var visual = (GameObject)PrefabUtility.InstantiatePrefab(model);
            visual.transform.SetParent(root.transform, false);
            visual.transform.localScale = Vector3.one * scale;
            var renderers = visual.GetComponentsInChildren<MeshRenderer>();
            var material = CreateMaterial(textureId, AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath));
            foreach (var renderer in renderers) renderer.sharedMaterials = new[] { material };
            if (renderers.Length == 0) throw new Exception(id + ": model has no renderer.");
            var bounds = renderers[0].bounds;
            foreach (var renderer in renderers.Skip(1)) bounds.Encapsulate(renderer.bounds);
            var collider = root.AddComponent<BoxCollider>();
            collider.center = bounds.center;
            collider.size = bounds.size;
            PrefabUtility.SaveAsPrefabAsset(root, Root + "/Prefabs/" + id + ".prefab");
        }
        finally { UnityEngine.Object.DestroyImmediate(root); }
        if (id != textureId) return;
        var iconImporter = (TextureImporter)AssetImporter.GetAtPath(Root + "/Models/" + id + "Icon.png");
        iconImporter.textureType = TextureImporterType.Sprite;
        iconImporter.spriteImportMode = SpriteImportMode.Single;
        iconImporter.alphaIsTransparency = true;
        iconImporter.mipmapEnabled = false;
        iconImporter.SaveAndReimport();
    }

    static Material CreateMaterial(string id, Texture2D texture)
    {
        var path = Root + "/Materials/" + id + "Atlas.mat";
        var shader = Shader.Find("HDRP/Lit");
        if (shader == null) throw new Exception("HDRP/Lit not available.");
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            material = new Material(shader) { name = id + "Atlas" };
            AssetDatabase.CreateAsset(material, path);
        }
        material.SetColor("_BaseColor", Color.white);
        material.SetTexture("_BaseColorMap", texture);
        material.SetFloat("_Metallic", id == "QuotaMug" ? .12f : id == "Ringhoffer240" ? .08f : 0);
        material.SetFloat("_Smoothness", id == "QuotaMug" ? .65f : id == "Ringhoffer240" ? .4f : .3f);
        material.SetFloat("_DoubleSidedEnable", 0);
        material.SetFloat("_CullMode", 2);
        material.SetFloat("_CullModeForward", 2);
        UnityEditor.Rendering.HighDefinition.HDShaderUtils.ResetMaterialKeywords(material);
        EditorUtility.SetDirty(material);
        return material;
    }
}
