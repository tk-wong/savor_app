import {Text, TextInput, View, TouchableOpacity, StyleSheet} from "react-native";
import {useState} from "react";

export default function Index() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    return (
        <View
            style={{
                flex: 1,
                justifyContent: "center",
                alignItems: "center",
            }}
        >

            <Text>Welcome</Text>
            <Text>User Name:</Text>
            <TextInput style={{borderWidth: 1}} placeholder={"User name"} onChangeText={setUsername}/>
            <Text>Password</Text>
            <TextInput style={{borderWidth: 1}} secureTextEntry={true} placeholder={"Password"}
                       onChangeText={setPassword}/>
            <TouchableOpacity onPress={() => {
                alert(`name: ${username}, password: ${password}`);
            }} style={style.button}>
                <Text>Submit</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => {
                alert("Create account")
            }} style={style.button}>
                <Text>Create account</Text>
            </TouchableOpacity>
        </View>
    );
}
const style = StyleSheet.create(
    {
        button: {
            alignItems: 'center',
            backgroundColor: '#DDDDDD',
            padding: 10,
        },
    }
)