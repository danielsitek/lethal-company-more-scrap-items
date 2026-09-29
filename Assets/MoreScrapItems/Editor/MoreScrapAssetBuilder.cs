using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
[InitializeOnLoad]
public static class MoreScrapAssetBuilder
{
    const string Root="Assets/MoreScrapItems";
    static MoreScrapAssetBuilder() { EditorApplication.delayCall += () => { if(File.Exists("build-more-scrap.request")) { File.Delete("build-more-scrap.request"); Build(); } }; }
    [MenuItem("Tools/More Scrap Items/Build models and scrap bundle")]
    public static void Build()
    {
        try {
            Directory.CreateDirectory(Root+"/Materials"); Directory.CreateDirectory(Root+"/Prefabs"); AssetDatabase.Refresh();
            MakeModel("QuotaMug",1.6f); MakeModel("MoonFrame",1.4f); AssetDatabase.SaveAssets();
            var paths=new[]{Root+"/Prefabs/QuotaMug.prefab",Root+"/Prefabs/MoonFrame.prefab",Root+"/Models/QuotaMugIcon.png",Root+"/Models/MoonFrameIcon.png"};
            Directory.CreateDirectory("Builds/MoreScrapItems");
            var result=BuildPipeline.BuildAssetBundles("Builds/MoreScrapItems",new[]{new AssetBundleBuild { assetBundleName="morescrapassets",assetNames=paths}},BuildAssetBundleOptions.ChunkBasedCompression|BuildAssetBundleOptions.StrictMode|BuildAssetBundleOptions.ForceRebuildAssetBundle,BuildTarget.StandaloneWindows64);
            if(result==null) throw new Exception("Bundle build failed.");
            var report=new List<string>();
            foreach(var path in paths.Take(2)) { var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(path); var tris=prefab.GetComponentsInChildren<MeshFilter>().Sum(m=>m.sharedMesh.triangles.Length/3); if(tris==0) throw new Exception("Empty model"); report.Add(prefab.name+" triangles="+tris); }
            File.WriteAllLines("Builds/MoreScrapItems/asset-validation.txt",report); Debug.Log("MORE_SCRAP_BUILD_COMPLETE");
        } catch(Exception e) { File.WriteAllText("more-scrap-build-error.txt",e.ToString()); Debug.LogException(e); }
    }
    static void MakeModel(string id,float scale)
    {
        var root=new GameObject(id); var visual=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Root+"/Models/"+id+".fbx"));
        visual.transform.SetParent(root.transform,false); visual.transform.localScale=Vector3.one*scale;
        foreach(var r in visual.GetComponentsInChildren<MeshRenderer>()) r.sharedMaterials=r.sharedMaterials.Select(CreateMaterial).ToArray();
        var bounds=new Bounds(Vector3.zero,Vector3.zero); foreach(var r in visual.GetComponentsInChildren<MeshRenderer>()) bounds.Encapsulate(r.bounds);
        var collider=root.AddComponent<BoxCollider>(); collider.center=bounds.center; collider.size=bounds.size;
        PrefabUtility.SaveAsPrefabAsset(root,Root+"/Prefabs/"+id+".prefab"); UnityEngine.Object.DestroyImmediate(root);
        var importer=(TextureImporter)AssetImporter.GetAtPath(Root+"/Models/"+id+"Icon.png"); importer.textureType=TextureImporterType.Sprite; importer.spriteImportMode=SpriteImportMode.Single; importer.alphaIsTransparency=true; importer.mipmapEnabled=false; importer.SaveAndReimport();
    }
    static Material CreateMaterial(Material source)
    {
        string name = source != null ? source.name.Replace(" (Instance)", "") : "EnamelCream";
        var path = Root + "/Materials/" + name + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if(material != null) return material;
        var shader = Shader.Find("HDRP/Lit");
        if(shader == null) throw new Exception("HDRP/Lit not available.");
        material = new Material(shader) { name = name };
        var colors = new Dictionary<string, Color> {
            {"EnamelCream",new Color(.84f,.79f,.65f)}, {"EnamelTeal",new Color(.025f,.29f,.31f)},
            {"QuotaInk",new Color(.035f,.055f,.05f)}, {"WalnutWood",new Color(.23f,.105f,.043f)},
            {"Brass",new Color(.61f,.36f,.11f)}, {"IvoryMat",new Color(.86f,.81f,.68f)},
            {"NightSky",new Color(.03f,.085f,.16f)}, {"AmberMoon",new Color(.95f,.52f,.18f)},
            {"DistantMountains",new Color(.14f,.33f,.39f)}, {"NearMountains",new Color(.04f,.20f,.23f)},
            {"Snow",new Color(.68f,.79f,.73f)}, {"FrameBacking",new Color(.12f,.09f,.058f)}
        };
        material.SetColor("_BaseColor", colors.ContainsKey(name) ? colors[name] : Color.white);
        material.SetFloat("_Metallic", name == "Brass" ? .72f : name.StartsWith("Enamel") ? .12f : 0);
        material.SetFloat("_Smoothness", name.StartsWith("Enamel") ? .7f : name == "Brass" ? .65f : .2f);
        // Flat printed art has no backside thickness; enable the HDRP double-sided mode.
        material.SetFloat("_DoubleSidedEnable",1);
        material.EnableKeyword("_DOUBLESIDED_ON"); material.SetFloat("_CullMode",0); material.SetFloat("_CullModeForward",0);
        UnityEditor.Rendering.HighDefinition.HDShaderUtils.ResetMaterialKeywords(material);
        AssetDatabase.CreateAsset(material,path);
        return material;
    }
}
