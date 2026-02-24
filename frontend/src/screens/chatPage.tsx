import React, { useState, useCallback, useEffect } from 'react'
import {Actions, ActionsProps, GiftedChat, IMessage, Send, SendProps} from 'react-native-gifted-chat'
import { useHeaderHeight } from '@react-navigation/elements'
import {View, Image, useColorScheme, Platform,} from "react-native";
import {Feather} from "@expo/vector-icons";
import {useSafeAreaInsets} from "react-native-safe-area-context";


export default function Example() {
    const [messages, setMessages] = useState<IMessage[]>([])
    const [listening,setlstening] = useState(false);
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

    const onSend = useCallback((messages:IMessage[] = []) => {
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

        <View style={{flex: 1}}>
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
            messagesContainerStyle={{
                paddingBottom: insets.bottom
            }}
        />
            {Platform.OS === 'android' && <View style={{ height: insets.bottom }} />}

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
        <Image
            style={{ width: 32, height: 32 }}
            source={require('../../assets/images/react-logo.png')}
        />
    </Send>
))
