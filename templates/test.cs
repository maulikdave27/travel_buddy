using UnityEngine;
using UnityEngine.Networking;
using SimpleJSON;

public class LightController : MonoBehaviour
{
    public Light pointLight;
    public Light directionalLight;
    public Camera mainCamera;
    public Camera secondCamera;
    public string blynkAPIUrl = "https://blr1.blynk.cloud/external/api/get?token=KK4JFjsIIeyK18Kl9kpyyxTKXn8eV1rk&dataStreamId=1";
    public string ledValueKey = "v0";

    void Update()
    {
        // Fetch LED value from Blynk API
        UnityWebRequest request = UnityWebRequest.Get(blynkAPIUrl);
        request.SendWebRequest().completed += (asyncOperation) =>
        {
            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.Log("Failed to fetch LED value: " + request.error);
                return;
            }

            // Parse JSON response
            JSONNode responseJson = JSON.Parse(request.downloadHandler.text);
            int ledValue = responseJson[ledValueKey].AsInt;

            // Turn on or off the point light based on the API value
            if (pointLight != null)
                pointLight.enabled = (ledValue == 1);

            // Toggle lights and cameras as before
            directionalLight.enabled = !pointLight.enabled;
            mainCamera.enabled = !pointLight.enabled;
            secondCamera.enabled = pointLight.enabled;
        };
    }
}
