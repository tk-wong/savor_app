import {FlatList, Image, ImageSourcePropType, ListRenderItem, Text, TouchableOpacity, View} from "react-native";
import {useState} from "react";

export default function AllRecipePage() {
    return <View>
        <Text>All Recipes</Text>
        <RecipeCard/>
    </View>
}

interface Recipe {
    id: number;
    name: string;
    image: ImageSourcePropType;
}

function RecipeCard() {
    const [recipe_list, setRecipeList] = useState<Recipe[]>(Array.from({length: 10}, (_, i) => {
                return {name: `Recipe ${i}`, id: i, image: require("../../assets/images/react-logo.png")}
            }
        )
    );
    // TODO: fetch recipe list from backend and display it in a card format

    //  useEffect(() => {
    //      const list = Array.from({ length: 11 }, (_, i) => `Recipe ${i}`);
    //      setRecipeList(list);
    //  }, []);
    // const message = recipe_list.map((recipe) => {
    //     return <Text>{recipe}</Text>
    // })
    const renderItem: ListRenderItem<Recipe> = ({item}) => {
        return <TouchableOpacity onPress={() => {console.log(`Recipe id: ${item.id}`)}}>
            <Image source={item.image} style={{width: 100, height: 100}}/>
            <Text>{item.name}</Text>
        </TouchableOpacity>
    };
    return (

        <FlatList data={recipe_list} renderItem={renderItem} numColumns={2}
                  keyExtractor={(item) => item.id.toString()}/>

    )
}



