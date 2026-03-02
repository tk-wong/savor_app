import { Feather } from "@expo/vector-icons";
import AntDesign from '@expo/vector-icons/AntDesign';
import { useHeaderHeight } from '@react-navigation/elements';
import React, { useCallback, useEffect, useState } from 'react';
import { Platform, useColorScheme, View } from "react-native";
import { Actions, ActionsProps, GiftedChat, IMessage, Send, SendProps } from 'react-native-gifted-chat';
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { getNewChatGroup, sendMessage } from "../api/chat";
import { isAxiosError } from "axios";

export default function ChatPage() {
    const [messages, setMessages] = useState<IMessage[]>([])
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
                text: 'Hello developer',
                createdAt: new Date(),
                user: {
                    _id: 2,
                    name: 'John Doe',
                    avatar: 'https://placeimg.com/140/140/any',
                },
            },
        ])
    }, [])

    const onSend = useCallback((messages: IMessage[] = []) => {
        if(messages.length === 0) {
            return;
        }
        if(chatGroupId === null) {
            getNewChatGroup().then((response) => {
                console.log("New chat group created with ID:", response.group_id);
                setChatGroupId(response.group_id);
            }).catch((error) => {
                console.error("Error creating new chat group:", error);
                if (isAxiosError(error)) {
                    console.error("Axios error details:", {
                        message: error.message,
                        response: error.response
                            ? {
                                status: error.response.status,
                                data: error.response.data,
                            }
                            : null,
                    });
                }
            })
            return;
        }
        sendMessage(messages[0].text, chatGroupId!).then((response) => {
            const botMessage: IMessage = {
                _id: Math.random(),
                text: response.prompt_type,
                createdAt: new Date(),
                user: {
                    _id: 2,
                    name: 'SavorBot',
                    avatar: 'https://placeimg.com/140/140/any',
                },
            }
            setMessages(previousMessages =>
                GiftedChat.append(previousMessages, [botMessage]),
            )
        }).catch((error) => {
            console.error("Error sending message:", error);
            if (isAxiosError(error)) {
                console.error("Axios error details:", {
                    message: error.message,
                    response: error.response
                    ? {
                        status: error.response.status,
                        data: error.response.data,
                    }
                    : null,
                });
            }
            return;
        })
        setMessages(previousMessages =>
            GiftedChat.append(previousMessages, messages),
        )
    }, [])
    const RenderActions = React.memo((props: ActionsProps) => {
        const colorScheme = useColorScheme()
        const isDark = colorScheme === 'dark'

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
                icon={() => (
                    <Feather
                        name={listening ? 'mic' : 'mic-off'}
                        size={24}
                        color={listening ? '#ff4444' : '#666'}
                        onPress={() => setlstening(!listening)}
                    />
                )}
                options={{
                    'Choose From Library': () => {
                        console.log('Choose From Library')
                    },
                    Cancel: () => {
                        console.log('Cancel')
                    },
                }}
                optionTintColor={isDark ? '#ffffff' : '#222B45'}
            />
        )
    })
    return (

        <View style={{ flex: 1 }}>
            <GiftedChat
                messages={messages}
                onSend={messages => {
                    onSend(messages);
                }}
                user={{
                    _id: 1,
                }}
                keyboardAvoidingViewProps={{ keyboardVerticalOffset: keyboardVerticalOffset }}
                renderSend={RenderSend}
                // renderComposer={renderComposer}
                renderActions={RenderActions}

            // minInputToolbarHeight={60}
            // messagesContainerStyle={{
            //     paddingBottom: insets.bottom
            // }}
            />
            {Platform.OS === 'android' && <View />}

        </View>
    )
}

export const RenderSend = React.memo((props: SendProps<IMessage>) => (
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
        <AntDesign name="send" size={24} color="white" />
    </Send>
))

// TODO: implement voice interaction using react-native-voice or any other library, and connect it with the chat interface to allow users to send messages using their voice.
// TODO: fetch chat history from backend and display it in the chat interface, and also send new messages to the backend to store them in the database.
// TODO: send the user's message to the backend and get a response from the chatbot, and display the chatbot's response in the chat interface.