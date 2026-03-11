import {Feather} from "@expo/vector-icons";
import AntDesign from '@expo/vector-icons/AntDesign';
import {useHeaderHeight} from '@react-navigation/elements';
import React, {Dispatch, SetStateAction, useCallback, useEffect, useState} from 'react';
import {Alert, Platform, useColorScheme, View} from "react-native";
import {Actions, ActionsProps, GiftedChat, IMessage, MessageTextProps, Send, SendProps} from 'react-native-gifted-chat';
import {useSafeAreaInsets} from "react-native-safe-area-context";
import {getNewChatGroup, sendMessage} from "../api/chat";
import {ApiRequestError} from "../api/apiRequestError";
import {ExpoSpeechRecognitionModule, useSpeechRecognitionEvent} from "expo-speech-recognition";
import {ExpoSpeechRecognitionPermissionResponse} from "expo-speech-recognition/src/ExpoSpeechRecognitionModule.types";
import Markdown from "react-native-markdown-display";
import {useTextToSpeech} from "@/src/hooks/useTextToSpeech";
import {Stack, useRouter} from "expo-router";
import {MaterialDesignIcons} from '@react-native-vector-icons/material-design-icons';

function HeaderRightButton({clearChat}: {clearChat: () => void}) {
    const router = useRouter()
    return (
        <View style={{flexDirection: "row"}}>
            <AntDesign name={"history"} size={24} onPress={() => router.navigate("/chatHistoryPage")}/>
            <MaterialDesignIcons name={"chat-plus-outline"} size={24} onPress={clearChat}/>
        </View>
    );
}
//
// const useMessage = (): [IMessage[], Dispatch<SetStateAction<IMessage[]>>]  => {
//     const [messages, setMessages] = useState<IMessage[]>([]);
//     return [messages, setMessages];
// }

export default function ChatPage() {
    const [messages, setMessages] = useState<IMessage[]>([]);
    const [listening, setlstening] = useState(false);
    const [chatGroupId, setChatGroupId] = useState<number | null>(null);
    const headerHeight = useHeaderHeight();
    const insets = useSafeAreaInsets();
    const keyboardVerticalOffset = Platform.select({
        ios: headerHeight + insets.bottom,
        android: headerHeight, // Android often handles it better with just the header height
    });

    useEffect(() => {
        setMessages([
            {
                _id: 1,
                text: 'Hello **developer**',
                createdAt: new Date(),
                user: {
                    _id: 2,
                    // name: 'John Doe',
                    // avatar: 'https://placeimg.com/140/140/any',
                },
            },
        ])
    }, [])

    // useSpeechRecognitionEvent("end", () => {
    //     setlstening(false);
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
    });

    const {speak, isSpeaking, stopSpeaking} = useTextToSpeech();
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

        const sendToBackend = (groupId: number) => {
            console.log("Group ID:", groupId);
            sendMessage(messageText, groupId).then((response) => {
                setMessages(previousMessages =>
                    GiftedChat.append(previousMessages, [sanitizedMessage]),
                )
                if (!response || !response.prompt_type) {
                    console.warn("Invalid response from backend:", response);
                    Alert.alert("Error", "Received invalid response from server. Please try again.");
                    return;
                }
                if (response.prompt_type === "question") {
                    const message_text = response.answer;
                } else if (response.prompt_type === "recipe") {

                    const recipe = response.recipe;
                    const recipe_title = recipe.name;
                    const recipe_description = recipe.description;
                    const recipe_ingredients = recipe.ingredients.join("\n");
                    const recipe_instructions = recipe.instructions.join("\n");
                    const recipe_tips = recipe.tips.join("\n");
                    const messageText = `Here's a recipe for you:\n\n
                    Title: ${recipe_title}\n\n
                    Description:\n${recipe_description}\n\n
                    Ingredients:\n${recipe_ingredients}\n\n
                    Instructions:\n${recipe_instructions}\n\n
                    Tips:\n${recipe_tips}`;
                } else {
                    Alert.alert("Unknown response type", `Received unknown prompt type from server`);
                    console.warn("Unknown prompt type in response:", response);
                    return;
                }


                const botMessage: IMessage = {
                    _id: Math.random(),
                    text: messageText,
                    createdAt: new Date(),
                    user: {
                        _id: "bot",
                        name: 'SavorBot',
                    },
                }
                setMessages(previousMessages =>
                    GiftedChat.append(previousMessages, [botMessage]),
                )
                if (listening) {
                    ExpoSpeechRecognitionModule.stop();
                    setlstening(false);
                    const cleanedText = messageText.replace(/[^\p{L}\p{N}\s]/gu, '');
                    speak(cleanedText).then();
                }
            }).catch((error: ApiRequestError) => {
                console.error("Error sending message:", error.message);
                Alert.alert(`Error Code: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while sending message.");

            })
        };

        if (chatGroupId === null) {
            getNewChatGroup().then((response) => {
                console.log("New chat group created with ID:", response.group_id);
                setChatGroupId(response.group_id);
                sendToBackend(response.group_id);
            }).catch((error: ApiRequestError) => {
                console.error("Error creating new chat group:", error.message);
                Alert.alert(`Error Code: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while creating chat group.");
            })
        } else {
            sendToBackend(chatGroupId);
        }
    }, [chatGroupId])
    const renderActions = React.memo((props: ActionsProps) => {
        const colorScheme = useColorScheme()
        const isDark = colorScheme === 'dark'

        const loadIcon = () => {
            const toggleVoiceRecognition = () => {
                setlstening(!listening);
                const handleVoiceRecognition = (result: ExpoSpeechRecognitionPermissionResponse) => {
                    if (!result.granted) {
                        console.warn("Permissions not granted", result);
                        return;
                    }
                    if (!listening) {
                        ExpoSpeechRecognitionModule.start({
                            lang: "en-US",
                            interimResults: true,
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
    const renderMessageText = (props: MessageTextProps<IMessage>) => {
        if (props.currentMessage) {
            return <Markdown>
                {props.currentMessage.text}
            </Markdown>
        }
        return null
    }
    return (
        <>
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Chat with SavorBot",
                    headerRight: () => <HeaderRightButton clearChat={() => setMessages([])}/>

                }}
            />
            <View style={{flex: 1}}>
                <GiftedChat
                    messages={messages}
                    onSend={messages => {
                        onSend(messages);
                    }}
                    user={{
                        _id: 1,
                    }}
                    keyboardAvoidingViewProps={{keyboardVerticalOffset: keyboardVerticalOffset}}
                    renderSend={renderSend}
                    // renderComposer={renderComposer}
                    renderActions={renderActions}

                    // minInputToolbarHeight={60}
                    // messagesContainerStyle={{
                    //     paddingBottom: insets.bottom
                    // }}
                    renderAvatar={null}
                    renderMessageText={renderMessageText}
                />
                {Platform.OS === 'android' && <View/>}

            </View>
        </>
    )
}

export const renderSend = React.memo((props: SendProps<IMessage>) => (
    <Send
        {...props}
        // isDisabled={!(props.text)}
        containerStyle={{
            width: 44,
            height: 44,
            alignItems: 'center',
            justifyContent: 'center',
            marginHorizontal: 4,
        }}
    >
        <AntDesign name="send" size={24} color="white"/>
    </Send>
))

// TODO: fetch chat history from backend and display it in the chat interface, and also send new messages to the backend to store them in the database.