import { Feather } from "@expo/vector-icons";
import AntDesign from '@expo/vector-icons/AntDesign';
import { useHeaderHeight } from '@react-navigation/elements';
import React, { useCallback, useState } from 'react';
import { Alert, Platform, useColorScheme, View } from "react-native";
import {
    Actions,
    ActionsProps,
    Bubble,
    Day,
    GiftedChat,
    IMessage,
    MessageTextProps,
    Send,
    SendProps
} from 'react-native-gifted-chat';
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { getChatHistoryByGroupId, getNewChatGroup, sendMessage } from "../api/chat";
import { ApiRequestError } from "../api/apiRequestError";
import { ExpoSpeechRecognitionModule, useSpeechRecognitionEvent } from "expo-speech-recognition";
import { ExpoSpeechRecognitionPermissionResponse } from "expo-speech-recognition/src/ExpoSpeechRecognitionModule.types";
import Markdown from "react-native-markdown-display";
import { useTextToSpeech } from "@/src/hooks/useTextToSpeech";
import { useFocusEffect, useLocalSearchParams, useRouter } from "expo-router";
import { MaterialDesignIcons } from '@react-native-vector-icons/material-design-icons';
import { ChatResponse } from "@/src/types/response";
import { DetailRecipe, Ingredient } from "@/src/types";
import { cssInterop } from "nativewind";
import { StyledHeader } from "@/src/components/styledHeader";

cssInterop(MaterialDesignIcons, {
    className: {
        target: "style",
        nativeStyleToProp: { color: true },
    },
})

function HeaderRightButton({ clearChat }: { clearChat: () => void }) {
    const router = useRouter()
    return (
        <View className={"flex-row gap-2 p-2"}>
            <AntDesign name={"history"} size={24} onPress={() => router.navigate("/chatHistoryPage")}
                className={"!color-on-surface"} accessibilityHint={"chat history"} />
            <MaterialDesignIcons name={"chat-plus-outline"} size={24} onPress={clearChat}
                accessibilityHint={"new chat"} className={"!color-on-surface"} />
        </View>
    );
}

const normalizeEscapedNewlines = (value: string) => value.replace(/\\n/g, "\n");

const toBulletList = (items?: string[]) => {
    if (!Array.isArray(items) || items.length === 0) {
        return "- N/A";
    }
    return items
        .map((item) => `- ${normalizeEscapedNewlines(String(item ?? "").trim())}`)
        .join("\n");
};

const toNumberedList = (items?: string[]) => {
    console.log("Formatting numbered list:", items);
    if (!Array.isArray(items) || items.length === 0) {
        return "1. N/A";
    }
    return items
        .map((item, index) => `${index + 1}. ${normalizeEscapedNewlines(String(item ?? "").trim())}`)
        .join("\n");
};

const toIngredientList = (ingredients?: Array<Ingredient | string>) => {
    console.log("Formatting ingredient list:", ingredients);
    if (!Array.isArray(ingredients) || ingredients.length === 0) {
        return "- N/A";
    }

    return ingredients.map((ingredient) => {
        if (typeof ingredient === "string") {
            return `- ${normalizeEscapedNewlines(ingredient.trim())}`;
        }

        const ingredientName = normalizeEscapedNewlines(String(ingredient?.name ?? "").trim());
        const quantity = normalizeEscapedNewlines(String(ingredient?.quantity ?? "").trim());

        if (quantity && ingredientName) {
            return `- ${quantity} ${ingredientName}`;
        }
        if (ingredientName) {
            return `- ${ingredientName}`;
        }
        if (quantity) {
            return `- ${quantity}`;
        }
        return "- N/A";
    }).join("\n");
};

const buildRecipeMarkdown = (recipe: DetailRecipe) => {
    const recipeTitle = String(recipe?.title ?? "");
    const recipeDescription = normalizeEscapedNewlines(String(recipe?.description ?? ""));
    const recipeIngredients = toIngredientList(recipe?.ingredients);
    const recipeInstructions = toNumberedList(recipe?.directions);
    const recipeTips = toBulletList(recipe?.tips);

    return [
        "Here's a recipe for you:",
        "",
        `## ${recipeTitle}`,
        "",
        "**Description**",
        recipeDescription,
        "",
        "**Ingredients**",
        recipeIngredients,
        "",
        "**Instructions**",
        recipeInstructions,
        "",
        "**Tips**",
        recipeTips,
    ].join("\n");
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

const placeholderRecipeImageUrl = "https://blocks.astratic.com/img/general-img-square.png";

//
// const useMessage = (): [IMessage[], Dispatch<SetStateAction<IMessage[]>>]  => {
//     const [messages, setMessages] = useState<IMessage[]>([]);
//     return [messages, setMessages];
// }

export default function ChatPage() {
    const [messages, setMessages] = useState<IMessage[]>([]);
    const [listening, setListening] = useState(false);
    const [chatGroupId, setChatGroupId] = useState<number | null>(null);
    const headerHeight = useHeaderHeight();
    const insets = useSafeAreaInsets();
    const keyboardVerticalOffset = Platform.select({
        ios: headerHeight + insets.bottom,
        android: headerHeight, // Android often handles it better with just the header height
    });

    // useEffect(() => {
    //     setMessages([
    //         {
    //             _id: 1,
    //             text: 'Hello **developer**',
    //             createdAt: new Date(),
    //             user: {
    //                 _id: 2,
    //                 // name: 'John Doe',
    //                 // avatar: 'https://placeimg.com/140/140/any',
    //             },
    //         },
    //     ])
    // }, [])

    const params = useLocalSearchParams();
    useFocusEffect(useCallback(() => {
        const initialChatGroupId = params.chatGroupId ? parseInt(params.chatGroupId as string, 10) : null;
        if (initialChatGroupId) {
            setChatGroupId(initialChatGroupId);
            console.log("Loaded chat group ID from params:", initialChatGroupId);
            getChatHistoryByGroupId(initialChatGroupId).then((response) => {
                const backendBaseUrl = process.env.EXPO_PUBLIC_BACKEND_URL ?? "";
                const history = Array.isArray(response?.chat_history) ? response.chat_history : [];
                const sortedHistory = history.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
                const formattedMessages = sortedHistory.map((msg) => {
                    console.log(msg);
                    let responseText: string = "";
                    let responseImage: string | undefined = undefined;
                    let isRecipeMessage = false;

                    // Parse stored response JSON and format it like backend responses
                    let storedResponse;
                    try {
                        storedResponse = typeof msg.response === "string" ? JSON.parse(msg.response) : msg.response;
                    } catch (e) {
                        // Fallback for plain text responses
                        storedResponse = null;
                    }

                    if (storedResponse?.prompt_type === "question") {
                        responseText = normalizeEscapedNewlines(storedResponse.answer || "");
                    } else if (storedResponse?.prompt_type === "recipe") {
                        isRecipeMessage = true;
                        const recipe = storedResponse.recipe;
                        console.log("recipe:", recipe)
                        if (recipe) {
                            responseImage = buildImageUrl(backendBaseUrl, recipe.image_url ?? msg.image_url);
                            responseText = buildRecipeMarkdown(recipe);
                        } else {
                            responseText = "";
                        }
                    } else {
                        responseText = typeof msg.response === "string" ? msg.response : JSON.stringify(msg.response);
                    }

                    if (!responseImage) {
                        responseImage = buildImageUrl(backendBaseUrl, msg.image_url);
                    }
                    if (!responseImage && isRecipeMessage) {
                        responseImage = placeholderRecipeImageUrl;
                    }

                    return ([
                        {
                            _id: msg.id + 0.5, // Ensure unique ID for response message
                            text: responseText,
                            createdAt: new Date(msg.timestamp),
                            user: {
                                _id: "bot",
                                name: 'SavorBot',
                            },
                            image: responseImage,
                        },
                        {
                            _id: msg.id,
                            text: msg.prompt,
                            createdAt: new Date(msg.timestamp),
                            user: {
                                _id: 1
                            }
                        },
                    ])
                });
                const fullMessageList: IMessage[] = formattedMessages.flat();
                setMessages(fullMessageList);
            })
        } else {
            console.log("No chat group ID in params, starting with new chat.");
        }
    }, []))
    // useSpeechRecognitionEvent("end", () => {
    //     setListening(false);
    // });
    useSpeechRecognitionEvent("result", (event) => {
        const transcript = event.results[0]?.transcript;
        console.log(transcript);
        if (transcript) {
            const newMessage: IMessage = {
                _id: Math.random(),
                text: transcript,
                createdAt: new Date(),
                user: {
                    _id: 1,
                    name: 'User',
                },
            }
            onSend([newMessage]);
        }
        setListening(false)
    });

    const { speak } = useTextToSpeech();
    const onSend = useCallback((newMessages: IMessage[] = []) => {
        const outgoingMessage = newMessages[0];
        const messageText = typeof outgoingMessage?.text === "string" ? outgoingMessage.text.trim() : "";

        if (!outgoingMessage || messageText.length === 0) {
            return;
        }

        const sanitizedMessage: IMessage = {
            ...outgoingMessage,
            text: messageText,
        };

        const rollbackOptimisticMessage = () => {
            setMessages((previousMessages) => previousMessages.filter((message) => message._id !== sanitizedMessage._id));
        };

        // Optimistically show the user's message before network round-trips.
        setMessages((previousMessages) => GiftedChat.append(previousMessages, [sanitizedMessage]));

        const sendToBackend = (groupId: number) => {
            console.log("Group ID:", groupId);
            const handleMessageResponse = (response: ChatResponse) => {
                if (!response || !response.prompt_type) {
                    console.warn("Invalid response from backend:", response);
                    rollbackOptimisticMessage();
                    Alert.alert("Error", "Received invalid response from server. Please try again.");
                    return;
                }
                console.log(response);
                let response_text: string = "";
                let recipe_url: string | undefined = undefined;
                if (response.prompt_type === "question") {
                    response_text = normalizeEscapedNewlines(response.answer);
                } else if (response.prompt_type === "recipe") {
                    const recipe = response.recipe;
                    if (!recipe) {
                        rollbackOptimisticMessage();
                        Alert.alert("Error", "Received invalid recipe data from server. Please try again.");
                        return;
                    }

                    recipe_url = buildImageUrl(process.env.EXPO_PUBLIC_BACKEND_URL ?? "", recipe.image_url);
                    if (!recipe_url) {
                        recipe_url = placeholderRecipeImageUrl;
                    }
                    response_text = buildRecipeMarkdown(recipe);
                } else {
                    rollbackOptimisticMessage();
                    Alert.alert("Unknown response type", `Received unknown prompt type from server`);
                    console.warn("Unknown prompt type in response:", response);
                    return;
                }

                const botMessage: IMessage = {
                    _id: Math.random(),
                    text: response_text,
                    createdAt: new Date(),
                    user: {
                        _id: "bot",
                        name: 'SavorBot',
                    },
                    image: recipe_url,
                }
                setMessages(previousMessages =>
                    GiftedChat.append(previousMessages, [botMessage]),
                )
                if (listening) {
                    ExpoSpeechRecognitionModule.stop();
                    setListening(false);
                    const cleanedText = messageText.replace(/[^\p{L}\p{N}\s]/gu, '');
                    speak(cleanedText).then();
                }
            };
            const handleMessageError = (error: ApiRequestError) => {
                console.error("Error sending message:", error.message);
                rollbackOptimisticMessage();
                Alert.alert(`Error Code: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while sending message.");

            };
            sendMessage(messageText, groupId).then(handleMessageResponse).catch(handleMessageError)
        };

        if (chatGroupId === null) {
            getNewChatGroup().then((response) => {
                console.log("New chat group created with ID:", response.group_id);
                setChatGroupId(response.group_id);
                sendToBackend(response.group_id);
            }).catch((error: ApiRequestError) => {
                console.error("Error creating new chat group:", error.message);
                rollbackOptimisticMessage();
                Alert.alert(`Error Code: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while creating chat group.");
            })
        } else {
            sendToBackend(chatGroupId);
        }
    }, [chatGroupId])
    const renderActions = React.memo((props: ActionsProps) => {

        const loadIcon = () => {
            const toggleVoiceRecognition = () => {
                setListening(!listening);
                const handleVoiceRecognition = (result: ExpoSpeechRecognitionPermissionResponse) => {
                    if (!result.granted) {
                        console.warn("Permissions not granted", result);
                        return;
                    }
                    if (!listening) {
                        ExpoSpeechRecognitionModule.start({
                            lang: "en-US",
                            interimResults: false,
                            continuous: false,
                        });
                    } else {
                        ExpoSpeechRecognitionModule.stop();
                    }
                };
                ExpoSpeechRecognitionModule.requestPermissionsAsync().then(handleVoiceRecognition).catch((error) => {
                    console.error("Error requesting permissions or starting/stopping speech recognition:", error);
                })
            };
            return (
                <Feather
                    name={listening ? 'mic' : 'mic-off'}
                    size={24}
                    color={listening ? '#ff4444' : '#666'}
                    onPress={toggleVoiceRecognition}
                />
            );
        };
        return (
            <Actions
                {...props as any}
                containerStyle={{
                    width: 44,
                    height: 44,
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginLeft: 4,
                    marginRight: 4,
                    marginBottom: 0,
                }}
                icon={loadIcon}
            // options={{
            //     'Choose From Library': () => {
            //         console.log('Choose From Library')
            //     },
            //     Cancel: () => {
            //         console.log('Cancel')
            //     },
            // }}
            // optionTintColor={isDark ? '#ffffff' : '#222B45'}
            />
        )
    })
    const isDarkMode = useColorScheme() === 'dark';
    const primaryColor = isDarkMode ? '#D0BCFF' : '#6750A4';
    const onPrimaryColor = isDarkMode ? '#381E72' : '#FFFFFF';
    const primaryContainerColor = isDarkMode ? '#4F378B' : '#EADDFF';
    const onPrimaryContainerColor = isDarkMode ? '#EADDFF' : '#4F378B';
    const surfaceContainerColor = isDarkMode ? '#36343B' : '#E6E0E9';
    const onSurfaceColor = isDarkMode ? '#E6E0E9' : '#1D1B20';
    const renderMessageText = (props: MessageTextProps<IMessage>) => {
        if (props.currentMessage) {
            return <Markdown style={{
                body: {
                    color: props.currentMessage.user._id === 1 ? onPrimaryColor : onPrimaryContainerColor,
                    fontFamily: "inter-regular",
                    fontSize: 16,
                },
                strong: {
                    color: props.currentMessage.user._id === 1 ? onPrimaryColor : onPrimaryContainerColor,
                    fontFamily: "inter-bold",
                    fontSize: 16,
                },
                heading: {
                    color: props.currentMessage.user._id === 1 ? onPrimaryColor : onPrimaryContainerColor,
                    fontFamily: "inter-bold",
                    fontSize: 18,
                }
            }}>
                {props.currentMessage.text}
            </Markdown>
        }
        return null
    }
    return (
        <>
            <StyledHeader title={"Chat with Savor bot"} options={{
                headerRight: () => <HeaderRightButton clearChat={() => {
                    setChatGroupId(null);
                    setMessages([])
                }} />

            }} />
            <View className={"flex-1"}>
                <GiftedChat
                    messages={messages}
                    onSend={messages => {
                        onSend(messages);
                    }}
                    user={{
                        _id: 1,
                    }}
                    keyboardAvoidingViewProps={{ keyboardVerticalOffset: keyboardVerticalOffset }}
                    renderSend={renderSend}
                    // renderComposer={renderComposer}
                    renderActions={renderActions}

                    // minInputToolbarHeight={60}
                    // messagesContainerStyle={{
                    //     paddingBottom: insets.bottom
                    // }}
                    renderAvatar={null}
                    renderMessageText={renderMessageText}
                    renderBubble={(props) => {
                        return (<Bubble {...props} wrapperStyle={{
                            left: {
                                backgroundColor: primaryContainerColor,
                                padding: 6,
                            },
                            right: {
                                backgroundColor: primaryColor,
                                padding: 6,
                            }
                        }} />)
                    }}
                    timeTextStyle={{
                        left: {
                            color: onPrimaryContainerColor,
                        },
                        right: {
                            color: onPrimaryColor,
                        }
                    }}
                    renderDay={(props) => {
                        return <Day {...props} wrapperStyle={{ backgroundColor: surfaceContainerColor }} textProps={{
                            style: {
                                color: onSurfaceColor,
                            }
                        }} />
                    }}
                />
                {Platform.OS === 'android' && <View />}

            </View>
        </>
    )
}

export const renderSend = React.memo((props: SendProps<IMessage>) => (
    <Send
        {...props}
        // isDisabled={!(props.text)}
        containerStyle={{
            minWidth: 44,
            minHeight: 44,
            alignItems: 'center',
            justifyContent: 'center',
            marginHorizontal: 4,
        }}
        textStyle={{
            marginBottom: 0,
            marginLeft: 0,
            marginRight: 0,
            backgroundColor: 'transparent',
            fontFamily: "inter-regular",
        }}
    >
        <View className={"items-center justify-center"}>
            <AntDesign name="send" size={24} className={"!color-on-surface"} />
        </View>
    </Send>
))

