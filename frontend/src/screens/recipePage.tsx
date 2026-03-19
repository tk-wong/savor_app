import {router, useFocusEffect, useLocalSearchParams} from "expo-router";
import {useCallback, useRef, useState} from "react";
import {Image, ScrollView, Text, TouchableOpacity, View} from "react-native";
import {SafeAreaView} from "react-native-safe-area-context";
import {DetailRecipe} from "../types";
import AntDesign from '@expo/vector-icons/AntDesign';
import {getRecipeById} from "@/src/api/recipe";
import {useTextToSpeech} from "@/src/hooks/useTextToSpeech";
import {
    ExpoSpeechRecognitionModule,
    ExpoSpeechRecognitionResultEvent,
    useSpeechRecognitionEvent
} from "expo-speech-recognition";
import {useSpeechToText} from "@/src/hooks/useSpeechToText";
import {StyledHeader} from "@/src/components/styledHeader";
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
    const params = useLocalSearchParams();
    console.log(`Received recipe id: ${params.id}`);

    const defaultRecipe: DetailRecipe = {
        id: 0,
        name: "Recipe not found",
        description: "",
        // Placeholder image
        ingredients: [],
        instructions: [],
        tips: [],
    };

    // const [recipe, setRecipe] = useState<DetailRecipe>( recipe_sample);

    const [recipe, setRecipe] = useState<DetailRecipe>(defaultRecipe);
    const [stepIndex, setStepIndex] = useState(-1);
    const [listening, setListening] = useState(false);
    const [voiceTranscript, setVoiceTranscript] = useState("");
    const {speak, stopSpeaking} = useTextToSpeech();
    const ttsLockRef = useRef(false);
    const waitMs = (ms: number) => new Promise<void>(res => setTimeout(res, ms));

    const {startListening, stopListening} = useSpeechToText();
    const fetchRecipeDetails = useCallback(() => {
        getRecipeById(Number(params.id)).then(
            (data) => {
                console.log("Fetched recipe details:", data);
                setRecipe({
                    id: data.recipe.id,
                    name: data.recipe.name,
                    description: data.recipe.description,
                    image_url: data.recipe.image_url, // Convert image URL to ImageSourcePropType
                    ingredients: data.recipe.ingredients,
                    instructions: data.recipe.instructions,
                    tips: data.recipe.tips,
                });
            }
        ).catch((error) => {
            console.error("Error fetching recipe details:", error);
            setRecipe(defaultRecipe);
        });
    }, []);
    useFocusEffect(fetchRecipeDetails);

    const speakStep = async (stepIndex: number, isButtonPress: boolean) => {
        console.log("Speaking step:", stepIndex);
        if (stepIndex >= 0 && stepIndex < recipe.instructions.length) {
            // Ensure STT is stopped before starting TTS, and restart afterwards.
            if (ttsLockRef.current) return; // already speaking
            if (!isButtonPress) {
                ttsLockRef.current = true;
            }
            const text = recipe.instructions[stepIndex];
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
    const startVoiceInteraction = async () => {
        console.log(`turn on voice assistant to read the recipe ${recipe.name} (id: ${recipe.id})`);
        setStepIndex(0);
        await speakStep(0, false);
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
        if (stepIndex + 1 <= recipe.instructions.length - 1) {
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
    const recipe_uri = recipe.image_url ? recipe.image_url : "https://blocks.astratic.com/img/general-img-square.png";
    return (
        <>
            <StyledHeader title={recipe.name}/>
            <SafeAreaView>
                <ScrollView className={"px-4 pb-safe-8 safe-pb-12"}>
                    <Image source={{uri: recipe_uri}}
                           className={"max-w-full w-full aspect-square rounded-xl p-safe-or-1"}/>
                    <Text
                        className={"global-text !font-italic !text-m text-on-surface text-center pb-4"}>{recipe.description}</Text>
                    <Text className={"global-text !font-bold !text-xl text-on-surface"}>Ingredients:</Text>
                    {recipe.ingredients.map((ingredient, index) => (
                        <Text key={index} className={"global-text text-on-surface pb-2"}>{ingredient}</Text>
                    ))}
                    <Text className={"global-text !font-bold !text-xl text-on-surface pt-4"}>Instructions:</Text>
                    {recipe.instructions.map((instruction, index) => {
                        const currentStepClass = stepIndex == index ? "text-red-500" : "text-on-surface";
                        return (<Text key={index}
                                      className={`global-text ${currentStepClass} pb-4`}>{`${index + 1}. ${instruction}`}</Text>)
                    })}
                    <Text className={"global-text !font-bold !text-xl text-on-surface pt-4"}>Tips:</Text>
                    {recipe.tips.map((tip, index) => (
                        <Text className={"global-text text-on-surface pb-4"} key={index}>{`${index + 1}. ${tip}`}</Text>
                    ))}
                    <TouchableOpacity onPress={() => {
                        console.log(`turn on voice assistant to read the recipe ${recipe.name} (id: ${recipe.id})`);
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
                            className={"global-text text-on-primary"}>{listening ? "stop voice interaction " : "start voice interaction"}</Text>
                    </TouchableOpacity>
                    <View className={"bg-surface-container rounded-xl p-4 my-4"}>
                        <Text className={"global-text color-on-surface"}>Step Navigations:</Text>
                        <View className={"flex-row justify-center align-middle"}>
                            <TouchableOpacity onPress={speakNextStep}
                                              className={"global-button bg-secondary !rounded  !p-2.5 !m-2.5 "}
                                              disabled={stepIndex >= recipe.instructions.length - 1}>
                                <AntDesign name="plus" size={24} className={"!color-on-secondary align-middle"}/>
                            </TouchableOpacity>
                            <TouchableOpacity onPress={speakPreviousStep}
                                              className={"global-button bg-secondary !rounded-[5px]  !p-2.5 !m-2.5"}
                                              disabled={stepIndex <= 0}>
                                <AntDesign name="minus" size={24} className={"!color-on-secondary align-middle"}/>
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