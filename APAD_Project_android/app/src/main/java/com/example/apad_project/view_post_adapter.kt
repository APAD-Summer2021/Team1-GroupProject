package com.example.apad_project

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.graphics.Bitmap
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.activity_view_post_adapter.view.*
import org.json.JSONArray

class view_post_adapter(
add: JSONArray,
description: JSONArray,
title: JSONArray,
theme: JSONArray,
user: JSONArray,
images: JSONArray,
bitmap_list: Array<Bitmap>
) : RecyclerView.Adapter<CustomViewHolder>() {

    val title_list = title
    override fun getItemCount(): Int {
        return title_list.length()
    }
    val add_list = add
    val desc_list = description
    val theme_list = theme
    val user_list = user
    val image_list = images
    val bitmapList = bitmap_list

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CustomViewHolder {
        val layoutInflater = LayoutInflater.from(parent?.context)
        val cellForRow = layoutInflater.inflate(R.layout.activity_view_post_adapter, parent, false)
        return CustomViewHolder(cellForRow)
    }

    override fun onBindViewHolder(holder: CustomViewHolder, position: Int) {
        val listTitles = title_list.get(position)
        val listAdd = add_list.get(position)
        val listDesc = desc_list.get(position)
        val listTheme = theme_list.get(position)
        val userList = user_list.get(position)
        val bitList = bitmapList[position]

        holder?.view?.textView_title.text  = "Title : " + listTitles.toString()
        holder?.view?.textView_desc?.text = "Description : " + listDesc.toString()
        holder?.view?.textView_add?.text = "Address : " + listAdd.toString()
        holder?.view?.textView_theme?.text = "Theme : " + listTheme.toString()
        holder?.view?.textView_user?.text = "Contact : " + userList.toString()
        holder?.view?.imageView_post.setImageBitmap(bitList)
    }
}

class CustomViewHolder(val view: View): RecyclerView.ViewHolder(view) {

}
