package com.example.apad_project

import android.graphics.Bitmap
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Base64
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.gson.GsonBuilder
import okhttp3.*
import java.io.IOException
import android.view.View
import kotlinx.android.synthetic.main.activity_view_post.*
import org.json.JSONArray
import org.json.JSONObject
import android.graphics.BitmapFactory;
import android.widget.*
import android.widget.ArrayAdapter

private var recyclerView: RecyclerView? = null
private val adapter: view_post_adapter? = null

class view_post : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_view_post)
        recyclerView = findViewById<View>(R.id.recyclerView_main) as RecyclerView
        recyclerView!!.layoutManager = LinearLayoutManager(this)
        fetchResponse()

    }
    fun fetchResponse() {
        println("Fetching data from API")
        var type = resources.getStringArray(R.array.view_pets_array)
        var new_type = "all"
        val spinner = findViewById<Spinner>(R.id.pets_spinner)
        if (spinner != null) {
            val adapter = ArrayAdapter(
                this,
                android.R.layout.simple_spinner_item, type
            )
            spinner.adapter = adapter

            spinner.onItemSelectedListener = object :
                AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    parent: AdapterView<*>,
                    view: View, position: Int, id: Long
                ) { new_type = type[position]

                    val apiURL = "https://apadphase3pethaven.uc.r.appspot.com/api/view_all?type="
                    if (new_type == "All"){
                        new_type ="all"
                    }
                    var new_URL = apiURL+new_type
                    val request = Request.Builder().url(new_URL).build()
                    val client = OkHttpClient()
                    client.newCall(request).enqueue(object : Callback {

                        override fun onResponse(call: Call, response: Response) {
                            val stringJson = response.body?.string()
                            println(stringJson)
                            val gsonBuild = GsonBuilder().create()
                            val add = JSONObject(stringJson).getJSONArray("address_values")
                            val description = JSONObject(stringJson).getJSONArray("description_values")
                            val title = JSONObject(stringJson).getJSONArray("title_values")
                            val theme = JSONObject(stringJson).getJSONArray("theme_values")
                            val user = JSONObject(stringJson).getJSONArray("user_id_values")
                            val images = JSONObject(stringJson).getJSONArray("image_values")
                            print("Here")
                            viewPosts(add, description, title, theme, user, images)

                            runOnUiThread {
                                val list_ofdecoded_images : MutableList<Bitmap> = mutableListOf()
                                for (i in 0 until user.length()) {
                                    val imageBytes =
                                        Base64.decode((images[i] as String).toByteArray(), Base64.DEFAULT)
                                    val decodedImage =
                                        BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
                                    list_ofdecoded_images.add(decodedImage)
                                }
//                        image.setImageBitmap(decodedImage)
                                println(list_ofdecoded_images.size)
                                val bitList : Array<Bitmap> = list_ofdecoded_images.toTypedArray()
//                    val temp = mapOf("list_of_images" to list_ofdecoded_images)
//                    val bitList = JSONArray(list_ofdecoded_images)
//                    val bitList = JSONObject(temp).getJSONArray("list_of_images")
//                    println(bitList)
                                recyclerView_main.adapter = view_post_adapter(add, description, title, theme, user, images,bitList)
//                    recyclerView_main.adapter = ViewPostAdapter(add, description, title, theme, user, images)
                            }
                        }

                        override fun onFailure(call: Call, e: IOException) {
                            println("Failed to fetch")
                        }
                    })

                }


                override fun onNothingSelected(parent: AdapterView<*>) {
                    // write code to perform some action
                }
            }
        }


    }

    private fun viewPosts(
        addy: JSONArray,
        description: JSONArray,
        title: JSONArray,
        theme: JSONArray,
        user: JSONArray,
        images: JSONArray
    ) {

        val numPosts = addy.length()

        // Will Need To Dynamically Create Views To Display on Fragment
        for (i in 0 until numPosts) {
            println("Address: " + addy.get(i).toString())
            println("Description: " + description.get(i).toString())
            println("Title: " + title.get(i).toString())
            println("Theme: " + theme.get(i).toString())
            println("User: " + user.get(i).toString())
//            println(images.get(i).toString())
            println("    ")
        }
    }
}