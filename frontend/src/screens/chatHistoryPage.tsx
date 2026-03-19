import {SafeAreaView} from "react-native-safe-area-context";
import {useFocusEffect, useRouter} from "expo-router";
import {useCallback, useState} from "react";
import {Alert, FlatList, Text, TouchableOpacity, View} from "react-native";
import {ApiRequestError} from "@/src/api/apiRequestError";
import {getAllChatGroups} from "@/src/api/chat";
import {ChatGroup} from "@/src/types/chatGroup";
import {format, parseISO} from "date-fns";
import {StyledHeader} from "@/src/components/styledHeader";

export default function ChatHistoryPage() {
    const [allChatGroups, setAllChatGroups] = useState<ChatGroup[]>([]);
    // useEffect(() => {
    //     setAllChatGroups([
    //         {
    //             id: 1,
    //             name: "Chat Group 1",
    //             last_edited: "2024-06-01T12:00:00Z"
    //         },
    //         {
    //             id: 2,
    //             name: "Chat Group 2",
    //             last_edited: "2024-06-02T15:30:00Z"
    //         }
    //     ])
    // }, []);
    useFocusEffect(useCallback(() => {
                getAllChatGroups().then(
                    (data) => {
                        setAllChatGroups(data.chat_groups);
                    }
                ).catch(
                    (error: ApiRequestError) => {
                        console.error("Error fetching chat groups:", error.message);
                        Alert.alert(`Error: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while fetching chat groups.");
                    }
                )
            }, []
        )
    )
    return (
        <>
            <StyledHeader title={"Chat History"}/>
            <View  className={"gap-4 mx-auto w-full px-4 bg-surface pb-safe"}>
                <FlatList
                    data={allChatGroups}
                    keyExtractor={(item) => item.id.toString()}
                    renderItem={({item}) => {
                        const date = parseISO(item.last_edited)
                        const formatDate = format(date, "do, MMM yyyy")
                        return (<TouchableOpacity onPress={() => {
                                const router = useRouter();
                                console.log(`Chat group id: ${item.id}`);
                                router.push({pathname: `/chatPage`, params: {chatGroupId: item.id}})
                            }} className={"flex-1 gap-1 pb-4 px-2"}>
                                <Text className={"global-text !text-on-surface !text-xl"}>{item.name}</Text>
                                <Text className={"global-text !text-on-surface-variant !text-sm"}>{formatDate}</Text>
                            </TouchableOpacity>
                        )
                    }}
                    className={"gap-4 mx-auto w-full px-4 bg-surface p-safe"}
                >
                </FlatList>
            </View>
        </>
    )
}