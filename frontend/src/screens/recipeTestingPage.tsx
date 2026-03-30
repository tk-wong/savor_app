import { router, useLocalSearchParams } from "expo-router";
import { useRef, useState } from "react";
import { Image, ScrollView, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { DetailRecipe } from "../types";
import AntDesign from '@expo/vector-icons/AntDesign';
import { useTextToSpeech } from "@/src/hooks/useTextToSpeech";
import {
    ExpoSpeechRecognitionModule,
    ExpoSpeechRecognitionResultEvent,
    useSpeechRecognitionEvent
} from "expo-speech-recognition";
import { useSpeechToText } from "@/src/hooks/useSpeechToText";
import { StyledHeader } from "@/src/components/styledHeader";
// interface SampleDetailRecipe {
//     id: number;
//     name: string;
//     description: string;
//     image: ImageSourcePropType;
//     ingredients: string[];
//     instructions: string[];
//     tips: string[];
// }

export default function RecipePage() {
    const recipe_sample: DetailRecipe = {
        id: 1,
        title: "Spaghetti Carbonara",
        description: "A classic Italian pasta dish made with eggs, cheese, pancetta, and black pepper.",
        // image_url: require("../../assets/images/react-logo.png"),
        ingredients: [
            "200g spaghetti",
            "100g pancetta",
            "2 large eggs",
            "50g pecorino cheese",
            "50g parmesan cheese",
            "2 cloves of garlic",
            "Salt and black pepper to taste"
        ],
        directions: [
            "Cook the spaghetti in a large pot of salted boiling water until al dente.",
            "In a pan, cook the pancetta with the garlic until crispy. Remove the garlic and discard.",
            "In a bowl, beat the eggs and mix in the pecorino and parmesan cheese.",
            "Drain the spaghetti and add it to the pan with the pancetta. Remove from heat.",
            "Quickly pour the egg and cheese mixture over the pasta, tossing quickly to prevent scrambling.",
            "Season with salt and black pepper to taste. Serve immediately."
        ],
        tips: [
            "Use fresh eggs for the best flavor and texture.",
            "Pecorino cheese adds a sharper flavor, while parmesan is milder. You can adjust the ratio to your taste.",
            "Make sure to toss the pasta quickly with the egg mixture to create a creamy sauce without scrambling the eggs."
        ]
    };
    const params = useLocalSearchParams();
    console.log(`Received recipe id: ${params.id}`);

    const [recipe] = useState<DetailRecipe>(recipe_sample);
    const [stepIndex, setStepIndex] = useState(-1);
    const [listening, setListening] = useState(false);
    const [voiceTranscript, setVoiceTranscript] = useState("");
    const { speak, stopSpeaking } = useTextToSpeech();
    const { startListening, stopListening } = useSpeechToText();

    // small helper and lock to avoid races when toggling between TTS and STT
    const ttsLockRef = useRef(false);
    const waitMs = (ms: number) => new Promise<void>(res => setTimeout(res, ms));

    const speakStep = async (stepIndex: number, isButtonPress: boolean) => {
        console.log("Speaking step:", stepIndex);
        if (stepIndex >= 0 && stepIndex < recipe.directions.length) {
            // Ensure STT is stopped before starting TTS, and restart afterwards.
            if (ttsLockRef.current) return; // already speaking
            if (!isButtonPress) {
                ttsLockRef.current = true;
            }
            const text = recipe.directions[stepIndex];
            try {
                setListening(false);
                try {
                    stopListening();
                } catch (e) {
                    console.error(e);
                }
                await speak(text);
            } catch (err) {
                console.error('Error during speakStep:', err);
            } finally {
                // small delay to allow audio focus to settle before starting STT again
                await waitMs(150);
                if (!isButtonPress) { // if this was triggered by a button press, we don't want to auto-restart STT
                    setListening(true);
                    try {
                        startListening();
                    } catch (e) {
                        console.error(e);
                    }
                }
                ttsLockRef.current = false;

            }
        }
    };
    useSpeechRecognitionEvent("end", () => {
        // only auto-restart STT if we're not in the middle of TTS
        if (listening && !ttsLockRef.current) {
            console.log("Restarting voice interaction after speech ended");
            setTimeout(() => startVoiceInteraction(), 100);
        }
    })
    const speechResultHandler = (event: ExpoSpeechRecognitionResultEvent) => {
        const transcript = event.results[0]?.transcript.toLowerCase();
        setVoiceTranscript(transcript)
        console.log("Recognized speech:", transcript);
        if (transcript.includes("next step") || transcript.includes("next")) {
            speakNextStep()
        } else if (transcript.includes("previous step") || transcript.includes("previous") || transcript.includes("back")) {
            speakPreviousStep()
        } else if (transcript.includes("repeat")) {
            repeatStep()
        } else if (transcript.includes("reset")) {
            resetStep();
        }
    };
    useSpeechRecognitionEvent("result", speechResultHandler)
    const startVoiceInteraction = () => {
        console.log(`turn on voice assistant to read the recipe ${recipe.title} (id: ${recipe.id})`);
        startListening()
    }
    const speakPreviousStep = async () => {
        await stopSpeaking();
        const isButtonPress = !listening;
        if (stepIndex - 1 >= 0) {
            const nextIndex = stepIndex - 1;
            if (!isButtonPress) {
                setListening(false);
                try {
                    stopListening();
                } catch (e) {
                    console.error(e);
                }
            }
            setStepIndex(nextIndex);
            await speakStep(nextIndex, isButtonPress);
        }
    };
    const speakNextStep = async () => {
        await stopSpeaking();
        if (stepIndex + 1 <= recipe.directions.length - 1) {
            const isButtonPress = !listening;
            const nextIndex = stepIndex + 1;
            if (!isButtonPress) {
                setListening(false);
                try {
                    stopListening();
                } catch (e) {
                    console.error(e);
                }
            }
            setStepIndex(nextIndex);
            await speakStep(nextIndex, isButtonPress);
        }
    };
    const resetStep = async () => {
        await stopSpeaking();
        const isButtonPress = !listening;
        if (!isButtonPress) {
            setListening(false);
            try {
                stopListening();
            } catch (e) {
                console.error(e);
            }
        }
        setStepIndex(-1);
        // await speakStep(0, isButtonPress);
    };
    const repeatStep = async () => {
        await stopSpeaking();
        const isButtonPress = !listening;
        if (!isButtonPress) {
            setListening(false);
            try {
                stopListening();
            } catch (e) {
                console.error(e);
            }
        }
        await speakStep(stepIndex, isButtonPress);
    };
    const placeholder_image = "https://blocks.astratic.com/img/general-img-square.png";
    const recipe_uri = recipe.image_url ? process.env.EXPO_PUBLIC_BACKEND_URL + recipe.image_url : placeholder_image
    return (
        <>
            <StyledHeader title={recipe.title} />
            <SafeAreaView>
                <ScrollView className={"px-4 pb-safe-8 safe-pb-12"}>
                    <Image source={{ uri: recipe_uri }}
                        className={"max-w-full w-full aspect-square rounded-xl p-safe-or-1"} />
                    <Text
                        className={"global-text !font-italic !text-m text-on-surface text-center pb-4"}>{recipe.description}</Text>
                    <Text className={"global-text !font-bold !text-xl text-on-surface"}>Ingredients:</Text>
                    {recipe.ingredients.map((ingredient, index) => (
                        <Text key={index} className={"global-text text-on-surface pb-2"}>{ingredient}</Text>
                    ))}
                    <Text className={"global-text !font-bold !text-xl text-on-surface pt-4"}>Instructions:</Text>
                    {recipe.directions.map((instruction, index) => {
                        const currentStepClass = stepIndex == index ? "text-red-500" : "text-on-surface";
                        return (<Text key={index}
                            className={`global-text ${currentStepClass} pb-4`}>{`${index + 1}. ${instruction}`}</Text>)
                    })}
                    <Text className={"global-text !font-bold !text-xl text-on-surface pt-4"}>Tips:</Text>
                    {recipe.tips.map((tip, index) => (
                        <Text className={"global-text text-on-surface pb-4"} key={index}>{`${index + 1}. ${tip}`}</Text>
                    ))}
                    <TouchableOpacity onPress={() => {
                        console.log(`turn on voice assistant to read the recipe ${recipe.title} (id: ${recipe.id})`);
                        const previousState = listening;
                        setListening(!listening);
                        if (!previousState) {
                            startVoiceInteraction();
                        } else {
                            setListening(false);
                            ExpoSpeechRecognitionModule.stop();
                        }
                    }} className={"global-button !bg-primary"}>
                        <Text
                            className={"global-text text-on-primary"}>
                            {listening ? "stop voice interaction " : "start voice interaction"}
                        </Text>
                    </TouchableOpacity>
                    <View className={"bg-surface-container rounded-xl p-4 my-4"}>
                        <Text className={"global-text color-on-surface"}>Step Navigations:</Text>
                        <View className={"flex-row justify-center align-middle"}>
                            <TouchableOpacity onPress={speakNextStep}
                                className={"global-button bg-secondary !rounded  !p-2.5 !m-2.5 "}
                                disabled={stepIndex >= recipe.directions.length - 1}>
                                <AntDesign name="plus" size={24} className={"!color-on-secondary align-middle"} />
                            </TouchableOpacity>
                            <TouchableOpacity onPress={speakPreviousStep}
                                className={"global-button bg-secondary !rounded-[5px]  !p-2.5 !m-2.5"}
                                disabled={stepIndex <= 0}>
                                <AntDesign name="minus" size={24} className={"!color-on-secondary align-middle"} />
                            </TouchableOpacity>
                            <TouchableOpacity onPress={repeatStep}
                                className={"global-button bg-secondary !rounded-[5px]  !p-2.5 !m-2.5"}>
                                <Text className={"global-text !color-on-secondary"}>Repeat</Text>
                            </TouchableOpacity>
                            <TouchableOpacity onPress={resetStep}
                                className={"global-button bg-secondary !rounded-[5px]  !p-2.5 !m-2.5"}>
                                <Text className={"global-text !color-on-secondary"}>Reset</Text>
                            </TouchableOpacity>
                            <TouchableOpacity onPress={stopSpeaking}
                                className={"global-button bg-secondary !rounded-[5px]  !p-2.5 !m-2.5"}>
                                <Text className={"global-text !color-on-secondary"}>Stop</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                    <View className={"pb-6 mb-4"}>
                        <TouchableOpacity onPress={() => {
                            router.back();
                        }} className={"global-button !bg-primary-container !p-2.5-or-safe !m-2.5-or-safe "}>
                            <Text className={"global-text color-on-primary-container"}>Back</Text>
                        </TouchableOpacity>
                    </View>
                </ScrollView>
            </SafeAreaView>
        </>
    )
}