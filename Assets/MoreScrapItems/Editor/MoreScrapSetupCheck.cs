using System.IO;
using UnityEditor;
using UnityEngine;

[InitializeOnLoad]
public static class MoreScrapSetupCheck
{
    static MoreScrapSetupCheck() { EditorApplication.delayCall += Check; }

    static void Check()
    {
        const string marker = "Library/MoreScrapSetupVerified.txt";
        if (File.Exists(marker)) return;
        var pipeline = UnityEngine.Rendering.GraphicsSettings.currentRenderPipeline;
        if (pipeline == null || !pipeline.GetType().Name.Contains("HDRenderPipeline"))
        {
            Debug.LogError("MoreScrap setup: assign an HDRP pipeline in Graphics Settings.");
            return;
        }
        File.WriteAllText(marker, "Unity=" + Application.unityVersion + "\nPipeline=" + pipeline.GetType().Name);
        Debug.Log("MoreScrap setup verified: Unity and HDRP.");
    }
}
