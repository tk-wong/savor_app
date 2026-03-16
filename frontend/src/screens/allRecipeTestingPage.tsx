import {useHeaderHeight} from "@react-navigation/elements";
import {router} from "expo-router";
import React, {useEffect, useMemo, useState} from "react";
import {
    FlatList,
    Image,
    ImageSourcePropType,
    ListRenderItem,
    Platform,
    Text,
    TouchableOpacity, useWindowDimensions,
    View
} from "react-native";
import {SafeAreaView, useSafeAreaInsets} from "react-native-safe-area-context";
import {StyledHeader} from "@/src/components/styledHeader";

export default function AllRecipePage() {
    const headerHeight = useHeaderHeight();
    const insets = useSafeAreaInsets();
    // const keyboardVerticalOffset = Platform.select({
    //     ios: headerHeight + insets.bottom,
    //     android: headerHeight, // Android often handles it better with just the header height
    // });
    return (<>
        <StyledHeader title={"All Recipes"}/>
        <SafeAreaView>
            <RecipeCard/>
            {Platform.OS === 'android' && <View style={{height: insets.bottom}}/>}
        </SafeAreaView>
    </>)
}

interface RecipeCardItem {
    id: number;
    name: string;
    image: ImageSourcePropType;
}

function RecipeCard() {
    const [recipeList, setRecipeList] = useState<RecipeCardItem[]>([]);
    const { width } = useWindowDimensions();
    const numColumns = useMemo(() => {
        const idealItemWidth = 180; // most phones can fit 2 items at 180px, tablets can fit more
        const columns = Math.floor(width / idealItemWidth);
        return Math.min(4, Math.max(2, columns)); // force 2–4 columns range
    }, [width]);
    // useFocusEffect(useCallback(() => {
    //     console.log("Fetching all recipes");
    //     getAllRecipes().then((data) => {
    //         const formattedRecipes = data.recipes.map((recipe: Recipe) => ({
    //             id: recipe.id,
    //             name: recipe.title,
    //             image: { uri: recipe.image_url }, // Convert image URL to ImageSourcePropType
    //         }));
    //         setRecipeList(formattedRecipes);
    //     }).catch((error: ApiRequestError) => {
    //         console.error("Error fetching recipes:", error.message);
    //         Alert.alert(`Error: ${error.status ?? "Unknown"}`, error.message ?? "Unknown error occurred while fetching all recipes.");
    //     })
    // },[]));
    useEffect(() => {
        setRecipeList(Array.from({length: 20}, (_, i) => ({
            id: i + 1,
            name: `Spaghetti Carbonara with cheese`,
            image: require("../../assets/images/react-logo.png") // Use a local placeholder image
        })))
    }, []);
    const renderItem: ListRenderItem<RecipeCardItem> = ({item}) => {
        return (
            <View className={"flex-1 mx-3 items-center"}>
                <TouchableOpacity onPress={() => {
                    console.log(`Recipe id: ${item.id}`);
                    router.push({pathname: `/recipePage`, params: {id: item.id}})
                }
                }

                >
                    <Image source={{uri: "https://blocks.astratic.com/img/general-img-square.png"}}
                           className={"max-w-full w-full aspect-square rounded-xl"}/>
                    <Text className={"mt-2 text-center text-sm global-text text-on-surface"}>{item.name}</Text>
                </TouchableOpacity>
            </View>
        )
    };
    return (
        <FlatList data={recipeList} renderItem={renderItem} numColumns={numColumns}
                  key={numColumns}
                  keyExtractor={(item) => item.id.toString()}
                  contentContainerClassName={"gap-4 px-4 pb-6"}
                  columnWrapperClassName={"gap-4"}
        />
    )
}



