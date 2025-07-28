import { Inventory } from "@/app/page";
import { BACKEND_URL } from "@/config/config";
import axios from "axios";
import { useEffect, useState } from "react";



export function useInventory(){
    const [inventory, setInventory] = useState<Inventory[]>([]);


    useEffect(() => {
        const fetchData = async() => {
            const response = await axios.get(`${BACKEND_URL}/api/inventory`);
            const data = response.data
            console.log("the data is ", data)
        }

        fetchData()
    }, [])

    return {
        inventory
    }
}