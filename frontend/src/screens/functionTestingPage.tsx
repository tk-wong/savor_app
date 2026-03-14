import {Stack, useRouter} from 'expo-router';
import * as Speech from 'expo-speech';
import {Button, Pressable, StyleSheet, Text, TouchableOpacity} from "react-native";
import {SafeAreaView} from "react-native-safe-area-context";
import "../../global.css";
// import styles = module;
import {useTextToSpeech} from "../hooks/useTextToSpeech"
import {Styleeheader} from "@/src/components/styleeheader";
export default function FunctionTestingPage() {
    const router = useRouter();
    const speak = () => {
        const thingToSay = 'testing 123';
        Speech.speak(thingToSay,
            {
                language: "en-US",
                rate: 0.8,
            });
    };

    return (
        <>
           <Styleeheader title={"Function Testing Page"}/>
            <SafeAreaView className="flex gap-4 mx-auto">
                <TouchableOpacity onPress={() => {
                    // for debugging
                    router.navigate("/chatPage")
                }
                } style={style.button}>
                    <Text>Chat page</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={()=>router.navigate("/chatHistoryPage")} style={style.button}>
                    <Text>Chat history page</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    router.navigate("/speechTestingPage")
                }} style={style.button}>
                    <Text>speech to text and text to speech testing</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={() => {
                    // for debugging
                    router.navigate("/allRecipePage")
                }

                } style={style.button}>

                    <Text>All recipes page</Text>
                </TouchableOpacity>
                <Pressable onPress={() => {
                    // for debugging
                    router.push({pathname: `/recipePage`, params: {id: 1}})
                }

                } style={style.button}>

                    <Text>Recipe page</Text>
                </Pressable>
                {/* <TouchableOpacity onPress={() => {
                // for debugging
                testUser().then((data) => {
                    Alert.alert("User information", `data: ${JSON.stringify(data)}`);
                    console.log(data);
                }).catch((error) => {
                    Alert.alert("Error", `error: ${error}`);
                })
            }

            } style={style.button}>

                <Text>Recipe page</Text>
            </TouchableOpacity> */}
                <TouchableOpacity onPress={() => {
                    // for debugging
                    router.back()
                }

                } style={style.button}>

                    <Text>Back to Login page</Text>
                </TouchableOpacity>
                <Text className="text-xl font-bold text-blue-500">
                    Welcome to Nativewind!
                </Text>
                <Button title={"testing 123"} onPress={speak}/>
                <TouchableOpacity style={style.button} onPress={() => router.navigate("/recipeTestingPage")}>
                    <Text>Recipe TTS and STT testing</Text>
                </TouchableOpacity>
            </SafeAreaView>
        </>
    );
}
const style = StyleSheet.create(
    {
        button: {
            alignItems: 'center',
            backgroundColor: '#DDDDDD',
            padding: 20,
        },
    }
)