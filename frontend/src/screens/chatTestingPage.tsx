import {Feather} from "@expo/vector-icons";
import AntDesign from '@expo/vector-icons/AntDesign';
import {useHeaderHeight} from '@react-navigation/elements';
import React, {useCallback, useEffect, useState} from 'react';
import {Platform, useColorScheme, View} from "react-native";
import {Actions, ActionsProps, GiftedChat, IMessage, MessageTextProps, Send, SendProps} from 'react-native-gifted-chat';
import {SafeAreaView, useSafeAreaInsets} from "react-native-safe-area-context";
import {ExpoSpeechRecognitionModule, useSpeechRecognitionEvent} from "expo-speech-recognition";
import {ExpoSpeechRecognitionPermissionResponse} from "expo-speech-recognition/src/ExpoSpeechRecognitionModule.types";
import Markdown from "react-native-markdown-display";
import {useTextToSpeech} from "@/src/hooks/useTextToSpeech";
import {Stack, useLocalSearchParams, useRouter} from "expo-router";
import {MaterialDesignIcons} from '@react-native-vector-icons/material-design-icons';
import {cssInterop} from "nativewind";
import {StyledHeader} from "@/src/components/styledHeader";

function HeaderRightButton({clearChat}: { clearChat: () => void }) {
    const router = useRouter()
    return (
        <View style={{flexDirection: "row"}}>
            <AntDesign name={"history"} size={24} onPress={() => router.navigate("/chatHistoryTestingPage")} className={"bg-primary"}/>
            <MaterialDesignIcons name={"chat-plus-outline"} size={24} onPress={clearChat}
                                 accessibilityHint={"new chat"}/>
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
        setMessages([{
            _id: 2,
            text: 'Hello **user**',
            createdAt: new Date("2024-06-01T12:01:00Z"),
            user: {
                _id: 1,
                // name: 'John Doe',
                // avatar: 'https://placeimg.com/140/140/any',
            },
        },
            {
                _id: 1,
                text: 'Hello **developer**',
                createdAt: new Date("2024-06-01T12:00:00Z"),
                user: {
                    _id: 2,
                    // name: 'John Doe',
                    // avatar: 'https://placeimg.com/140/140/any',
                },
            }
        ])
    }, [])

    const onSend = useCallback((newMessages: IMessage[] = []) => {
        setMessages(previousMessages =>
            GiftedChat.append(previousMessages, newMessages),
        )
    }, [])
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
        cssInterop(Markdown, {className: "style"})
        if (props.currentMessage) {
            return <Markdown>
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
                }}/>

            }}/>
            {/*<Stack.Screen*/}
            {/*    options={{*/}
            {/*        headerShown: true,*/}
            {/*        title: "Chat with SavorBot",*/}
            {/*        headerRight: () => <HeaderRightButton clearChat={() => {*/}
            {/*            setChatGroupId(null);*/}
            {/*            setMessages([])*/}
            {/*        }}/>*/}

            {/*    }}*/}
            {/*/>*/}
            <SafeAreaView style={{flex: 1}}>
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

            </SafeAreaView>
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

