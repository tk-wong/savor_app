import {router, Stack, useFocusEffect, useLocalSearchParams} from "expo-router";
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

    const [recipe,setRecipe] = useState<DetailRecipe>(defaultRecipe);
    const [stepIndex, setStepIndex] = useState(0);
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
    const startVoiceInteraction = () => {
        console.log(`turn on voice assistant to read the recipe ${recipe.name} (id: ${recipe.id})`);
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
        setStepIndex(0);
        await speakStep(0, isButtonPress);
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

    return (
        <>
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Recipe Details",
                    headerLeft: () => {
                        return <TouchableOpacity onPress={() => {
                            console.log("Back to all recipes");
                            router.back();
                        }} style={{padding: 10}}>
                            <AntDesign name="arrow-up" size={24} color="black"/>
                        </TouchableOpacity>
                    }
                }

                }
            />
            <SafeAreaView>
                <ScrollView>
                    <Text>{recipe.name}</Text>
                    {recipe.image_url ?
                        <Image source={{uri: recipe.image_url}} style={{width: 200, height: 200}}/>
                        :
                        <Image source={require("../../assets/images/react-logo.png")}
                               style={{width: 200, height: 200}}/>
                    }
                    <Text>{recipe.description}</Text>
                    <Text>Ingredients:</Text>
                    {recipe.ingredients.map((ingredient, index) => (
                        <Text key={index}>{ingredient}</Text>
                    ))}
                    <Text>Instructions:</Text>
                    {recipe.instructions.map((instruction, index) => (
                        <Text key={index}
                              style={{color: stepIndex == index ? 'red' : 'black'}}>{`${index + 1}. ${instruction}`}</Text>
                    ))}
                    <Text>Tips:</Text>
                    {recipe.tips.map((tip, index) => (
                        <Text key={index}>{`${index + 1}. ${tip}`}</Text>
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
                    }} style={{backgroundColor: "blue", padding: 10, margin: 10, borderRadius: 5}}>
                        <Text
                            style={{color: "white"}}>{listening ? "stop voice interaction " : "start voice interaction"}</Text>
                    </TouchableOpacity>
                    <View style={{flexDirection: "row"}}>
                        <TouchableOpacity onPress={speakNextStep}
                                          style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                            <AntDesign name="plus" size={24} color="black"/>
                        </TouchableOpacity>
                        <Text>{stepIndex}</Text>
                        <TouchableOpacity onPress={speakPreviousStep}
                                          style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                            <AntDesign name="minus" size={24} color="black"/>
                        </TouchableOpacity>
                        <TouchableOpacity onPress={repeatStep}
                                          style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                            <Text>Repeat</Text>
                        </TouchableOpacity>
                        <TouchableOpacity onPress={resetStep}
                                          style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                            <Text>Reset</Text>
                        </TouchableOpacity>
                        <TouchableOpacity onPress={stopSpeaking}
                                          style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                            <Text>Stop</Text>
                        </TouchableOpacity>
                    </View>
                    <TouchableOpacity onPress={() => {
                        router.back();
                    }} style={{backgroundColor: "green", padding: 10, margin: 10, borderRadius: 5}}>
                        <Text style={{color: "white"}}>return to all recipe</Text>
                    </TouchableOpacity>
                </ScrollView>
            </SafeAreaView>
        </>
    )
}