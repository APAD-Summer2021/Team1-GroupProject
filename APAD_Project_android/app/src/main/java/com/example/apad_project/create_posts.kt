package com.example.apad_project

//import com.example.apad_project.SecondFragmentArgs

import android.Manifest
import android.R.attr
import android.app.Activity
import android.content.ContentResolver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.drawable.BitmapDrawable
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.*
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.navArgs
import com.example.apad_project.databinding.FragmentCreatePostsBinding
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.fragment_create_posts.*
import kotlinx.android.synthetic.main.fragment_first.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okio.BufferedSink
import okio.source
import java.io.ByteArrayOutputStream
import java.io.IOException
import android.R.attr.data
import android.os.Build
import android.os.Environment
import android.util.Log
import androidx.annotation.RequiresApi
import java.io.File
import java.io.FileOutputStream
import okhttp3.*
import androidx.core.app.NotificationCompat.getGroup
import okhttp3.Headers.Companion.headersOf
import okhttp3.ResponseBody.Companion.create
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.Response
import okhttp3.OkHttpClient
import okhttp3.MultipartBody
import java.lang.Exception
import android.R.attr.bitmap
import android.util.Base64
import okhttp3.FormBody




/**
 * A simple [Fragment] subclass as the default destination in the navigation.
 */
class create_posts : Fragment(), LocationListener{

    private var _binding: FragmentCreatePostsBinding? = null
    private lateinit var locationManager: LocationManager
    private lateinit var tvGpsLocation: TextView
    private val locationPermissionCode = 2
    private val CAMERA_STUFF = 1
    private val CAMERA_PERMISSION_STUFF = 3
    var longitude = 0.0
    var latitude = 0.0

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!
    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        _binding = FragmentCreatePostsBinding.inflate(inflater, container, false)
        return binding.root
    }

    val args: create_postsArgs by navArgs()
    @RequiresApi(Build.VERSION_CODES.R)
    override fun onViewCreated(view: View, savedInstanceState: Bundle?){
        super.onViewCreated(view, savedInstanceState)
        super.onCreate(savedInstanceState)
        //setContentView(R.layout.fragment_first)
        val email = args.myArg1
        println("emailllllll "+email)
        var type = resources.getStringArray(R.array.pets_array)
        var title = view.findViewById(R.id.Title) as EditText
        var tags = view.findViewById(R.id.tags) as EditText
        var desc = view.findViewById(R.id.desc) as EditText
        var new_type = "Dog"
        //var btn_submit = view.findViewById(R.id.btn_submit) as Button
        view.findViewById<Button>(R.id.btnTakePic).setOnClickListener {
            if (ContextCompat.checkSelfPermission(
                    requireContext(),
                    Manifest.permission.CAMERA
                ) == PackageManager.PERMISSION_GRANTED
            ) {
                val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                startActivityForResult(intent, CAMERA_STUFF)
                println("intent "+intent)
            } else {
                ActivityCompat.requestPermissions(
                    requireActivity(),
                    arrayOf(Manifest.permission.CAMERA),
                    CAMERA_PERMISSION_STUFF
                )
            }

        }

        val button: Button = view.findViewById(R.id.getLocation)
        button.setOnClickListener {
            getLocation()
        }
        // access the spinner
        val spinner = view.findViewById<Spinner>(R.id.pets_spinner)

        if (spinner != null) {
            spinner.adapter = ArrayAdapter(
                requireActivity(),
                R.layout.support_simple_spinner_dropdown_item,
                resources.getStringArray(R.array.pets_array)
            )


            spinner.onItemSelectedListener = object :
                AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    parent: AdapterView<*>,
                    view: View, position: Int, id: Long
                ) {
                    new_type = type[position]
                    println("typeeeee "+new_type)
                }


                override fun onNothingSelected(parent: AdapterView<*>) {
                    // write code to perform some action
                }


            }
        }
        view.findViewById<Button>(R.id.btnSubmit).setOnClickListener {
            //println(type)
            val title= title.text.toString()
            val desc = desc.text.toString()
            val tags = tags.text.toString()
            val imageView = view?.findViewById<ImageView>(R.id.cameraImage)
            val bitmap = (imageView?.drawable as BitmapDrawable).bitmap
            println("imageView  "+imageView) // has base64
            println("bitmap  "+bitmap)
            println(email)
            println(title)
            println(desc)
            println(tags)
            println(new_type)
            println(this.longitude)
            println(this.latitude)
            println(this.cameraImage)
            println("imageee ")
            val longitude_s = this.longitude.toString()
            val latitude_s = this.latitude.toString()
            val user_id = "61075e23f8edb22b0d766477"
            sendPost(title,tags,desc,email,new_type,latitude_s,longitude_s,bitmap)
            println("helloo send is done")
           // findNavController().navigate(R.id.action_create_posts2_to_SecondFragment)

        }
    }

    @RequiresApi(Build.VERSION_CODES.R)
    fun sendPost(
        title: String,
        tags: String,
        desc: String,
        email: String,
        new_type: String,
        latitude: String,
        longitude: String,
        bitmap: Bitmap
    ){
        println("inside send post mthod")
        println("latitude "+latitude)
        println("longitude "+longitude)
        val byteArrayOutputStream = ByteArrayOutputStream()
//        bitmap.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream)
        bitmap.compress(Bitmap.CompressFormat.JPEG, 50, byteArrayOutputStream)

        val byteArray = byteArrayOutputStream.toByteArray()
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("title", title)
            .addFormDataPart("detailed_description", desc)
            .addFormDataPart("file", "filename.jpg",
                RequestBody.create("image/*jpg".toMediaTypeOrNull(), byteArray))
            .addFormDataPart("type", new_type)
            .addFormDataPart("tags", tags)
            .addFormDataPart("latitude", latitude)
            .addFormDataPart("longitude", longitude)
            .addFormDataPart("user", email)
            .build()

//        val encoded: String = Base64.encodeToString(byteArray, Base64.DEFAULT)
        val serverUrl = "https://apadphase3pethaven.uc.r.appspot.com/api/post_action"
//        val serverUrl = "https://5000-cs-139307086613-default.cs-us-central1-pits.cloudshell.dev/api/post_action"
//                "?user="+email+"&tags="+tags+"&detailed_description="+desc+"&type="+new_type+"&title="+title+"&latitude="+latitude+"&longitude="+longitude
//        val request = Request.Builder().url(serverUrl).build()
//        val formBody: RequestBody = FormBody.Builder().add("image", encoded).build()
        val request: Request = Request.Builder()
            .url(serverUrl)
            .post(requestBody)
            .build()

        println("requestttttttttttttttttttttttt "+ request)
        val client =OkHttpClient()
        client.newCall(request).enqueue(object:Callback{
            override fun onFailure(call: Call, e: IOException) {
                println("failed")
            }

            override fun onResponse(call: Call, response: Response) {
                val body =response?.body?.string()
                println("here is your response "+body)
//                Toast.makeText(context,"Successfully Posted to Server ",Toast.LENGTH_LONG).show()
            }
        })

    }

    private fun getLocation() {
        val locationManager = requireContext().getSystemService(Context.LOCATION_SERVICE) as LocationManager
        if ((ContextCompat.checkSelfPermission(requireContext(), Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED)) {
            ActivityCompat.requestPermissions(requireActivity(), arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), locationPermissionCode)
        }
        locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 5000, 5f, this)}

    override fun onLocationChanged(location: Location) {
        tvGpsLocation = requireView().findViewById(R.id.textView);
        tvGpsLocation.text = "Latitude: " + location.latitude + " , Longitude: " + location.longitude
        latitude = location.latitude
        longitude = location.longitude
        println(latitude)
        println(longitude)
    }
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        if (requestCode == locationPermissionCode) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            }
            else {
            }
        }
    }

    override fun  onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == CAMERA_STUFF && resultCode == Activity.RESULT_OK) {

            // Image Bitmap
            val image = data?.extras?.get("data") as Bitmap
            val imageCamera = view?.findViewById<ImageView>(R.id.cameraImage)
            imageCamera?.setImageBitmap(image)
            println("image bitmap "+image)
            println("image other value "+imageCamera)
        }
        else {
            super.onActivityResult(requestCode, resultCode, data)
        }

    }
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}