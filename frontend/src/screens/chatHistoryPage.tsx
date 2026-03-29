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
    const router = useRouter();

    const formatLastEditedDate = (lastEdited?: string) => {
        console.log(lastEdited);
        if (!lastEdited) {
            return "Unknown date";
        }

        const parsedDate = parseISO(lastEdited);
        if (Number.isNaN(parsedDate.getTime())) {
            return "Unknown date";
        }

        return format(parsedDate, "do, MMM yyyy");
    };
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
                        console.log(item)
                        const formatDate = formatLastEditedDate(item.last_edit)
                        return (<TouchableOpacity onPress={() => {
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