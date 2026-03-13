import {useCallback, useState} from "react";
import * as Speech from "expo-speech";

export const useTextToSpeech = () => {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const speak = useCallback(async (text:string, options = {}): Promise<void> => {
        // If already speaking, stop first to ensure a clean start.
        if (isSpeaking){
            try {
                await Speech.stop();
            } catch (err) {
                console.error('Error stopping previous speech:', err);
            }
        }
        setIsSpeaking(true);

        return await new Promise<void>((resolve, reject) => {
            try {
                Speech.speak(text, {
                    language: "en-US",
                    rate: 0.8,
                    ...options,
                    onDone: () => {
                        setIsSpeaking(false);
                        resolve();
                    },
                    onStopped: () => {
                        setIsSpeaking(false);
                        resolve();
                    },
                    onError: (err) => {
                        console.error("Speech error:", err);
                        setIsSpeaking(false);
                        reject(err);
                    }
                })
            } catch (err) {
                setIsSpeaking(false);
                reject(err as Error);
            }
        })
    }, [isSpeaking])

    // Always try to stop speech when requested. Don't rely on a stale `isSpeaking` value
    // (callbacks with empty deps capture the initial state). We call Speech.stop() and
    // ensure isSpeaking is set to false.
    const stopSpeak = useCallback(async () => {
        try {
            await Speech.stop();
        } catch (err) {
            console.error('Error stopping speech:', err);
        } finally {
            setIsSpeaking(false);
        }
    }, [])


    return {speak, isSpeaking, stopSpeaking: stopSpeak};
}