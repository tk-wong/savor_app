import {SafeAreaView} from "react-native-safe-area-context";
import {useState} from "react";
import {Alert, Text, TextInput, TouchableOpacity, View} from "react-native";
import {login} from "../api";
import {router} from "expo-router";
import {StyledHeader} from "@/src/components/styledHeader";

function LoginView() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")


    const loginHandler = () => {
        if (!email || !password) {
            Alert.alert("Error", "Please enter both email and password");
            return;
        }
        login(email, password).then((data) => {
            Alert.alert("Login successful");
            console.log(data);
            router.push("/chatPage");
        }).catch((error) => {
            Alert.alert("Login failed", `Error: ${error}`);
        });
    }
    return <SafeAreaView className={"flex-1 gap-4 mx-auto w-full px-4 bg-surface p-safe"}>
        <View className={" justify-between gap-2 p-4"}>
            <Text className={"global-text text-on-surface"}>Email:</Text>
            <TextInput
                className={"global-text-input border-on-surface-variant h-20 text-2xl text-on-surface-variant"}
                placeholder={"Enter your email"}
                onChangeText={setEmail}
                id={"username_input"}
                value={email}
                numberOfLines={1}

            />
        </View>
        <View className={"justify-between gap-2 p-4"}>
            <Text className={"global-text text-on-surface"}>Password:</Text>
            <TextInput
                className={"global-text-input border-on-surface-variant h-20 text-2xl text-on-surface-variant"}
                secureTextEntry={true}
                placeholder={"Enter your password"}
                onChangeText={setPassword} id={"password_input"}
                value={password}/>
        </View>
        <View className={"flex-1"}></View>
        <View className={"justify-between gap-4 p-4"}>
            <TouchableOpacity onPress={() => {
                // const message = "Create account"
                router.navigate("/createUserPage")
            }} className={"global-button bg-primary-container"}>
                <Text className={"global-text text-on-primary-container"}>Create account</Text>
            </TouchableOpacity>
            <View className={"flex-row gap-4 items-center align-middle"}>
            {/*<TouchableOpacity onPress={() => {*/}
            {/*    // const message = "Create account"*/}
            {/*    router.navigate("/createUserPage")*/}
            {/*}} className={"global-button bg-secondary dark:bg-transparent dark:border-white dark:border"}>*/}
            {/*    <Text className={"global-text text-on-secondary dark:text-white"}>Create account</Text>*/}
            {/*</TouchableOpacity>*/}
            {/*<View className={"flex-row gap-4 items-center align-middle"}>*/}
                <TouchableOpacity onPress={() => {
                    setEmail("");
                    setPassword("")
                }} className={"global-button !border !border-primary flex-1 !bg-transparent"}>
                    <Text className={"global-text !text-primary"}>Reset</Text>
                </TouchableOpacity>
                {/*<TouchableOpacity onPress={() => {*/}
                {/*    setEmail("");*/}
                {/*    setPassword("")*/}
                {/*}}*/}
                {/*                  className={"global-button  !bg-primary-container flex-1 dark:!bg-transparent dark:!border-white dark:!border"}>*/}
                {/*    <Text className={"global-text !text-on-primary-container dark:!text-white"}>Reset</Text>*/}
                {/*</TouchableOpacity>*/}
                {/*<TouchableOpacity onPress={*/}
                {/*    loginHandler*/}
                {/*} className={"global-button  !bg-primary flex-1 dark:!bg-transparent dark:!border-white dark:!border"}>*/}
                {/*    <Text className={"global-text !text-on-primary dark:!text-white"}>Submit</Text>*/}
                {/*</TouchableOpacity>*/}
                <TouchableOpacity onPress={
                    loginHandler
                } className={"global-button  !bg-primary flex-1 "}>
                    <Text className={"global-text !text-on-primary "}>Submit</Text>
                </TouchableOpacity>

            </View>
        </View>

        <TouchableOpacity onPress={() => {
            // for debugging
            router.push("/functionTestingPage")
        }} className={"global-button bg-gray-400"}>
            <Text className={"global-text"}>Function testing page</Text>
        </TouchableOpacity>

    </SafeAreaView>;
}

export default function LoginPage() {
    return (
        <>
            <StyledHeader title={"Welcome to Savor!"}/>
            <LoginView/>
        </>
    );
}

