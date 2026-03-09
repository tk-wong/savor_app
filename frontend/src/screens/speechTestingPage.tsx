import {SafeAreaView} from "react-native-safe-area-context";
import {ScrollView, Text, TouchableOpacity} from "react-native";
import * as Speech from "expo-speech";
import {style} from "@/src/style/globalStyle";
import React, {useState} from "react";
import {Feather} from "@expo/vector-icons";
import {listen} from "node:quic";
import {ExpoSpeechRecognitionModule, useSpeechRecognitionEvent} from "expo-speech-recognition";

export default function SpeechTestingPage(){
    const speak = () => {
        const thingToSay = 'testing 123';
        Speech.speak(thingToSay,
            {
                language: "en-US",
                rate: 0.8,
            });
    };
    const listen = () => {
        setListening(!listening)
    }

    const [listening, setListening] = useState(false);
    const [recognizing, setRecognizing] = useState(false);
    const [transcript, setTranscript] = useState("");

    useSpeechRecognitionEvent("start", () => setRecognizing(true));
    useSpeechRecognitionEvent("end", () => setRecognizing(false));
    useSpeechRecognitionEvent("result", (event) => {
        setTranscript(event.results[0]?.transcript);
    });
    useSpeechRecognitionEvent("error", (event) => {
        console.log("error code:", event.error, "error message:", event.message);
    });
    const handleStart = async () => {
        const result = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
        if (!result.granted) {
            console.warn("Permissions not granted", result);
            return;
        }
        // Start speech recognition
        ExpoSpeechRecognitionModule.start({
            lang: "en-US",
            interimResults: true,
            continuous: false,
        });
    };

    return (
        <SafeAreaView>
    <TouchableOpacity onPress={speak} style={style.button}>
        <Text>Press to test speech</Text>
    </TouchableOpacity>
            {!recognizing ? (
                <TouchableOpacity onPress={handleStart} style={style.button}>
                    <Text>Start</Text>
                    <Feather
                        name={'mic-off'}
                        size={24}
                        color={'#666'}
                    />
                </TouchableOpacity>
            ) : (
                <TouchableOpacity

                    onPress={() => ExpoSpeechRecognitionModule.stop()}
                >
                    <Text>Stop</Text>
                    <Feather
                        name={'mic' }
                        size={24}
                        color={'#ff4444' }
                    />
                </TouchableOpacity>
            )}

            <ScrollView>
                <Text>{transcript}</Text>
            </ScrollView>
        </SafeAreaView>
    )
}