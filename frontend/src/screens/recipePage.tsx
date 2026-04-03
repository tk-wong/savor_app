import { router, useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback, useRef, useState } from "react";
import { Image, ScrollView, Text, TouchableOpacity, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { DetailRecipe, Ingredient } from "../types";
import AntDesign from '@expo/vector-icons/AntDesign';
import { getRecipeById } from "@/src/api/recipe";
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
    const params = useLocalSearchParams();
    console.log(`[RecipePage] Loaded recipe screen for ID: ${params.id}`);

    const defaultRecipe: DetailRecipe = {
        id: 0,
        title: "Recipe not found",
        description: "",
        // Placeholder image
        ingredients: [],
        directions: [],
        tips: [],
    };

    const normalizeRecipe = (rawRecipe: Partial<DetailRecipe> | undefined): DetailRecipe => {
        const ingredients = Array.isArray(rawRecipe?.ingredients) ? rawRecipe.ingredients : [];
        const directions = Array.isArray(rawRecipe?.directions) ? rawRecipe.directions : [];
        const tips = Array.isArray(rawRecipe?.tips) ? rawRecipe.tips : [];

        return {
            id: Number(rawRecipe?.id ?? 0),
            title: String(rawRecipe?.title ?? "Recipe not found"),
            description: String(rawRecipe?.description ?? ""),
            image_url: rawRecipe?.image_url,
            ingredients,
            directions: directions,
            tips,
        };
    };

    // const [recipe, setRecipe] = useState<DetailRecipe>( recipe_sample);

    const [recipe, setRecipe] = useState<DetailRecipe>(defaultRecipe);
    const [stepIndex, setStepIndex] = useState(-1);
    const [listening, setListening] = useState(false);
    const [voiceInteractionActive, setVoiceInteractionActive] = useState(false);
    const [, setVoiceTranscript] = useState("");
    const { speak, stopSpeaking } = useTextToSpeech();
    const ttsLockRef = useRef(false);
    const voiceInteractionActiveRef = useRef(false);
    const [ttsActive, setTtsActive] = useState(false);
    const waitMs = (ms: number) => new Promise<void>(res => setTimeout(res, ms));

    const { startListening, stopListening } = useSpeechToText();
    const stepChangeLockRef = useRef(false);

    const setVoiceInteractionActiveState = (active: boolean) => {
        voiceInteractionActiveRef.current = active;
        setVoiceInteractionActive(active);
    };

    const fetchRecipeDetails = useCallback(() => {
        getRecipeById(Number(params.id)).then(
            (data) => {
                console.log(`[RecipePage] Recipe loaded successfully: ${data?.recipe?.title ?? "unknown title"}`);
                setRecipe(normalizeRecipe(data?.recipe));
            }
        ).catch((error) => {
            console.error(`[RecipePage] Failed to fetch recipe details for ID ${params.id}:`, error);
            setRecipe(defaultRecipe);
        });
    }, []);
    useFocusEffect(fetchRecipeDetails);

    const speakStep = async (stepIndex: number, isButtonPress: boolean) => {
        console.log(`[Voice] Speaking step ${stepIndex + 1}${isButtonPress ? " (manual)" : " (auto)"}`);
        const directions = recipe.directions;
        if (stepIndex >= 0 && stepIndex < directions.length) {
            // Ensure STT is stopped before starting TTS, and restart afterwards.
            if (ttsLockRef.current) return; // already speaking
            if (!isButtonPress) {
                ttsLockRef.current = true;
            }
            const text = directions[stepIndex];
            try {
                setTtsActive(true);
                setListening(false);
                try {
                    stopListening();
                } catch (e) {
                    console.warn("[Voice] Failed to stop listening before speaking step", e);
                }
                await speak(text);
            } catch (err) {
                console.error('[Voice] Error during speakStep:', err);
            } finally {
                // small delay to allow audio focus to settle before starting STT again
                await waitMs(150);
                if (!isButtonPress && voiceInteractionActiveRef.current) { // if this was triggered by a button press, we don't want to auto-restart STT
                    setListening(true);
                    try {
                        startListening();
                    } catch (e) {
                        console.warn("[Voice] Failed to restart listening after speaking step", e);
                    }
                }
                ttsLockRef.current = false;
                setTtsActive(false);

            }
        }
    };
    useSpeechRecognitionEvent("end", () => {
        // only auto-restart STT if we're not in the middle of TTS
        if (voiceInteractionActiveRef.current && listening && !ttsLockRef.current) {
            setTimeout(() => {
                try {
                    startListening();
                } catch (e) {
                    console.warn("[Voice] Failed to restart listening after speech end", e);
                }
            }, 100);
        }
    })
    const speechResultHandler = (event: ExpoSpeechRecognitionResultEvent) => {
        const transcript = event.results[0]?.transcript?.toLowerCase() ?? "";
        setVoiceTranscript(transcript)
        if (stepChangeLockRef.current) {
            return;
        }

        if (transcript.includes("next step") || transcript.includes("next")) {
            console.log("[Voice] Command recognized: next step");
            speakNextStep()
        } else if (transcript.includes("previous step") || transcript.includes("previous") || transcript.includes("back")) {
            console.log("[Voice] Command recognized: previous step");
            speakPreviousStep()
        } else if (transcript.includes("repeat")) {
            console.log("[Voice] Command recognized: repeat step");
            repeatStep()
        } else if (transcript.includes("reset")) {
            console.log("[Voice] Command recognized: reset step");
            resetStep();
        }
    };

    const lockStepChange = () => {
        stepChangeLockRef.current = true;
    };

    const unlockStepChange = () => {
        stepChangeLockRef.current = false;
    };

    useSpeechRecognitionEvent("result", speechResultHandler)
    const startVoiceInteraction = async () => {
        setVoiceInteractionActiveState(true);
        if (!Array.isArray(recipe.directions) || recipe.directions.length === 0) {
            try {
                setListening(true);
                startListening();
            } catch (e) {
                console.warn("[Voice] Failed to start listening with no directions", e);
            }
            return;
        }
        setStepIndex(0);
        // Let React commit the highlighted step text before starting TTS.
        await Promise.resolve();
        await speakStep(0, false);
    }
    const speakPreviousStep = async () => {
        lockStepChange();
        try {
            await stopSpeaking();
            const isButtonPress = !listening;
            if (stepIndex - 1 >= 0) {
                const nextIndex = stepIndex - 1;
                if (!isButtonPress) {
                    setListening(false);
                    try {
                        stopListening();
                    } catch (e) {
                        console.warn("[Voice] Failed to stop listening before previous step", e);
                    }
                }
                setStepIndex(nextIndex);
                await speakStep(nextIndex, isButtonPress);
            }
        } finally {
            unlockStepChange();
        }
    };
    const speakNextStep = async () => {
        lockStepChange();
        try {
            await stopSpeaking();
            const directions = recipe.directions;
            if (stepIndex + 1 <= directions.length - 1) {
                const isButtonPress = !listening;
                const nextIndex = stepIndex + 1;
                if (!isButtonPress) {
                    setListening(false);
                    try {
                        stopListening();
                    } catch (e) {
                        console.warn("[Voice] Failed to stop listening before next step", e);
                    }
                }
                setStepIndex(nextIndex);
                await speakStep(nextIndex, isButtonPress);
            }
        } finally {
            unlockStepChange();
        }
    };
    const resetStep = async () => {
        lockStepChange();
        try {
            await stopSpeaking();
            const isButtonPress = !listening;
            if (!isButtonPress) {
                setListening(false);
                try {
                    stopListening();
                } catch (e) {
                    console.warn("[Voice] Failed to stop listening before reset", e);
                }
            }
            setStepIndex(0);
            await speakStep(0, isButtonPress);
        } finally {
            unlockStepChange();
        }
    };
    const repeatStep = async () => {
        lockStepChange();
        try {
            await stopSpeaking();
            const isButtonPress = !listening;
            if (!isButtonPress) {
                setListening(false);
                try {
                    stopListening();
                } catch (e) {
                    console.warn("[Voice] Failed to stop listening before repeat", e);
                }
            }
            await speakStep(stepIndex, isButtonPress);
        } finally {
            unlockStepChange();
        }
    };

    const buildImageUrl = (base: string, imagePath?: string) => {
        if (!imagePath) {
            return undefined;
        }
        if (/^https?:\/\//i.test(imagePath)) {
            return imagePath;
        }

        const normalizedBase = String(base).replace(/\/+$/, "");
        let normalizedPath = String(imagePath).trim().replace(/\\/g, "/");
        if (normalizedBase.endsWith("/api") && normalizedPath.startsWith("/api/")) {
            normalizedPath = normalizedPath.slice(4);
        }
        if (!normalizedPath.startsWith("/")) {
            normalizedPath = `/${normalizedPath}`;
        }
        return `${normalizedBase}${normalizedPath}`;
    };

    const formatIngredient = (ingredient: Ingredient | string) => {
        if (typeof ingredient === "string") {
            return ingredient;
        }
        const ingredientName = String(ingredient?.name ?? "").trim();
        const quantity = String(ingredient?.quantity ?? "").trim();
        if (ingredientName && quantity) {
            return `${quantity} ${ingredientName}`;
        }
        return ingredientName || quantity || "N/A";
    };

    const placeholder_image = "https://blocks.astratic.com/img/general-img-square.png";
    const recipe_uri = buildImageUrl(process.env.EXPO_PUBLIC_BACKEND_URL ?? "", recipe.image_url) ?? placeholder_image;
    const ingredients = recipe.ingredients;
    const directions = recipe.directions;
    const tips = recipe.tips;
    const voiceToggleClassName = ttsActive
        ? "global-button !bg-surface-container !opacity-60"
        : "global-button !bg-primary";
    const voiceToggleTextClassName = ttsActive
        ? "global-text text-on-surface-variant"
        : "global-text text-on-primary";
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
                    {ingredients.map((ingredient, index) => (
                        <Text key={index} className={"global-text text-on-surface pb-2"}>{formatIngredient(ingredient)}</Text>
                    ))}
                    <Text className={"global-text !font-bold !text-xl text-on-surface pt-4"}>Instructions:</Text>
                    {directions.map((instruction, index) => {
                        const currentStepClass = stepIndex == index ? "text-red-500" : "text-on-surface";
                        return (<Text key={index}
                            className={`global-text ${currentStepClass} pb-4`}>{`${index + 1}. ${instruction}`}</Text>)
                    })}
                    <Text className={"global-text !font-bold !text-xl text-on-surface pt-4"}>Tips:</Text>
                    {tips.map((tip, index) => (
                        <Text className={"global-text text-on-surface pb-4"} key={index}>{`${index + 1}. ${tip}`}</Text>
                    ))}
                    <TouchableOpacity testID="voice-interaction-toggle" disabled={ttsActive} className={voiceToggleClassName} onPress={() => {
                        const previousState = voiceInteractionActive;
                        setVoiceInteractionActiveState(!previousState);
                        console.log(`[Voice] Voice interaction ${!previousState ? "started" : "stopped"} for recipe: ${recipe.title}`);
                        if (!previousState) {
                            startVoiceInteraction();
                        } else {
                            setListening(false);
                            void stopSpeaking();
                            ExpoSpeechRecognitionModule.stop();
                        }
                    }}>
                        <Text
                            className={voiceToggleTextClassName}>{voiceInteractionActive ? "stop voice interaction" : "start voice interaction"}</Text>
                    </TouchableOpacity>
                    <View className={"bg-surface-container rounded-xl p-4 my-4"}>
                        <Text className={"global-text color-on-surface"}>Step Navigations:</Text>
                        <View className={"flex-row justify-center align-middle"}>
                            <TouchableOpacity onPress={speakNextStep}
                                className={"global-button bg-secondary !rounded  !p-2.5 !m-2.5 "}
                                disabled={stepIndex >= directions.length - 1}>
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