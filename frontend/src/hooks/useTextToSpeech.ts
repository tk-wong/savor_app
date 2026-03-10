import {useCallback, useState} from "react";
import * as Speech from "expo-speech";

export const useTextToSpeech = () => {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const speak = useCallback(async (text:string, options = {}) => {
        if (isSpeaking){
            await Speech.stop();
        }
        setIsSpeaking(true);
        Speech.speak(text, {
            language: "en-US",
            rate: 0.8,
            ...options,
            onDone: () => {
                setIsSpeaking(false);
            },
            onStopped: () => {
                setIsSpeaking(false);
            },
            onError: (err) => {
                console.error("Speech error:", err);
                setIsSpeaking(false);
            }
        })
    }, [isSpeaking])
    return {speak, isSpeaking};
}