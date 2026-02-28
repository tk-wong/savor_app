import { Stack, useRouter } from 'expo-router';
import * as Speech from 'expo-speech';
import { Alert, StyleSheet, Text, TouchableOpacity } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { testUser } from "../api";

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
            <Stack.Screen
                options={{
                    headerShown: true,
                    title: "Function Testing",
                }}
            />
        <SafeAreaView>
            <TouchableOpacity onPress={() => {
                // for debugging
                router.navigate("/chatPage")
            }
            } style={style.button}>
                <Text>Chat page</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={speak} style={style.button}>
                <Text>Press to test speech</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
                // for debugging
                router.navigate("/allRecipePage")
            }

            } style={style.button}>

                <Text>All recipes page</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
                // for debugging
                router.navigate("/recipePage")
            }

            } style={style.button}>

                <Text>Recipe page</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
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
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
                // for debugging
                router.back()
            }

            } style={style.button}>

                <Text>Back to Login page</Text>
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