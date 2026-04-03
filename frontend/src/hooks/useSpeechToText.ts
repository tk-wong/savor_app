import {ExpoSpeechRecognitionModule} from "expo-speech-recognition";

export const  useSpeechToText= () =>{
    const startListening = () => {
        ExpoSpeechRecognitionModule.getPermissionsAsync().then(
            () =>   {
                ExpoSpeechRecognitionModule.start({
                    lang: "en-US",
                    interimResults: true,
                    continuous: false,
                    // androidIntentOptions: {
                    //
                    // }
                    androidIntentOptions: {
                        EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS: 5000,
                        EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS: 5000,
                    },
                })
            }
        ).catch((error) => {
            console.error("[Voice] Failed to start speech recognition:", error);
        });
    }
    const stopListening = () => {
        ExpoSpeechRecognitionModule.stop()
    }
    return { startListening, stopListening}
}