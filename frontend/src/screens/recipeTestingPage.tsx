import {router, Stack, useLocalSearchParams} from "expo-router";
import {useState} from "react";
import {Image, ScrollView, Text, TouchableOpacity, View} from "react-native";
import {SafeAreaView} from "react-native-safe-area-context";
import {DetailRecipe} from "../types";
import AntDesign from '@expo/vector-icons/AntDesign';
import {useTextToSpeech} from "@/src/hooks/useTextToSpeech";
import {ExpoSpeechRecognitionModule, useSpeechRecognitionEvent} from "expo-speech-recognition";
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
        name: "Spaghetti Carbonara",
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
        instructions: [
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

    const defaultRecipe: DetailRecipe = {
        id: 0,
        name: "Recipe not found",
        description: "",
        // Placeholder image
        ingredients: [],
        instructions: [],
        tips: [],
    };

    const [recipe, setRecipe] = useState<DetailRecipe>(recipe_sample);
    const [stepIndex, setStepIndex] = useState(0);
    const [listening, setListening] = useState(false);
    const [voiceTranscript, setVoiceTranscript] = useState("");
    // const [recipe, setRecipe] = useState<DetailRecipe>(defaultRecipe);

    // const fetchRecipeDetails = useCallback(() => {
    //     getRecipeById(Number(params.id)).then(
    //         (data) => {
    //             console.log("Fetched recipe details:", data);
    //             setRecipe({
    //                 id: data.recipe.id,
    //                 name: data.recipe.name,
    //                 description: data.recipe.description,
    //                 image_url: data.recipe.image_url, // Convert image URL to ImageSourcePropType
    //                 ingredients: data.recipe.ingredients,
    //                 instructions: data.recipe.instructions,
    //                 tips: data.recipe.tips,
    //             });
    //         }
    //     ).catch((error) => {
    //         console.error("Error fetching recipe details:", error);
    //         setRecipe(defaultRecipe);
    //     });
    // }, []);
    // useFocusEffect(fetchRecipeDetails);
    const {speak, isSpeaking, stopSpeaking} = useTextToSpeech();
    const speakStep = (stepIndex: number) => {
        console.log("Speaking step:", stepIndex);
        if (stepIndex >= 0 && stepIndex < recipe.instructions.length) {
            // Speech.speak(recipe.instructions[stepIndex], {
            //     language: "en-US",
            //     rate: 0.8,
            // });
            speak((recipe.instructions[stepIndex])).then()
        }
    };
    useSpeechRecognitionEvent("end", () => {
        if (listening) {
            console.log("Restarting voice interaction after speech ended");
            setTimeout(() => startVoiceInteraction(), 100);
        }
    })
    useSpeechRecognitionEvent("result", (event) => {
        const transcript = event.results[0]?.transcript.toLowerCase();
        setVoiceTranscript(transcript)
        console.log("Recognized speech:", transcript);
    })
    const startVoiceInteraction = () => {
        console.log(`turn on voice assistant to read the recipe ${recipe.name} (id: ${recipe.id})`);
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
            console.error(error);
        });
    }
    return (
        <>
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Recipe Details",
                    headerLeft : () =>{
                        return <TouchableOpacity onPress={() => {
                            console.log("Back to all recipes");
                            router.back();
                        }} style={{padding: 10}}>
                            <AntDesign name="arrow-up" size={24} color="black" />
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
                    <Image source={require("../../assets/images/react-logo.png")} style={{width: 200, height: 200}}/>
                }
                <Text>{recipe.description}</Text>
                <Text>Ingredients:</Text>
                {recipe.ingredients.map((ingredient, index) => (
                    <Text key={index}>{ingredient}</Text>
                ))}
                <Text>Instructions:</Text>
                {recipe.instructions.map((instruction, index) => (
                    <Text key={index} style={{color: stepIndex==index ? 'red':'black'}}>{`${index + 1}. ${instruction}`}</Text>
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
                <Text>{`Voice Transcript: ${voiceTranscript}`}</Text>
                <View style={{flexDirection: "row"}}>
                    <TouchableOpacity onPress={() => {
                        if (stepIndex + 1 <= recipe.instructions.length - 1) {
                            const nextIndex = stepIndex + 1;
                            setStepIndex(nextIndex);
                            speakStep(nextIndex);
                        }
                    }} style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                        <AntDesign name="plus" size={24} color="black"/>
                    </TouchableOpacity>
                    <Text>{stepIndex}</Text>
                    <TouchableOpacity onPress={() => {
                        if (stepIndex - 1 >= 0) {
                            const nextIndex = stepIndex - 1;
                            setStepIndex(nextIndex);
                            speakStep(nextIndex);
                        }
                    }} style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                        <AntDesign name="minus" size={24} color="black"/>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => {
                        speakStep(stepIndex);
                    }} style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                        <Text>Repeat</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => {
                        setStepIndex(0);
                    }} style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
                        <Text>Reset</Text>
                    </TouchableOpacity >
                    <TouchableOpacity onPress={stopSpeaking} style={{backgroundColor: "orange", padding: 10, margin: 10, borderRadius: 5}}>
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