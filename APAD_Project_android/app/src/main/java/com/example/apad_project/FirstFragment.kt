package com.example.apad_project

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.navigation.fragment.findNavController
import com.example.apad_project.databinding.FragmentFirstBinding
import okhttp3.*
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder


/**
 * A simple [Fragment] subclass as the default destination in the navigation.
 */
class FirstFragment : Fragment() {

    private var _binding: FragmentFirstBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    private val url = "http://" + "10.0.2.2" + ":" + 5000 + "/"
    private val postBodyString: String? = null
    private val mediaType: MediaType? = null
    private val requestBody: RequestBody? = null
    private val connect: Button? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root

    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        println("heloooo8888888888")

        binding.buttonSubmit.setOnClickListener {
            findNavController().navigate(R.id.action_FirstFragment_to_SecondFragment)
        }
        println("nooooooooooooooooooooooooooooooooooooooooooo")

        view.findViewById<Button>(R.id.button_submit).setOnClickListener{
            val email = view.findViewById<EditText>(R.id.editText_username).text.toString()
            val password = view.findViewById<EditText>(R.id.editTextTextPassword).text.toString()
            println("nooooooooooooooooooooooooooooooooooooooooooo")
            sendLogin(email,password)
            Toast.makeText(context,"hello you have logged in ",Toast.LENGTH_LONG).show()
            //val userId = "ObjectId('61028bc2231c32a0d4e5a581')"
            val action = FirstFragmentDirections.actionFirstFragmentToSecondFragment(email)
            findNavController().navigate(action)
            //findNavController().navigate(R.id.action_FirstFragment_to_SecondFragment)
        }


    }
    fun sendLogin(email: String, password: String){
        println("inside sendlogin "+ email +" "+ password)
        val url = "https://apadphase3pethaven.uc.r.appspot.com/api/login?email="+email+"&password="+password
        val request = Request.Builder().url(url).build()
        println("requestttttttttttttttttttttttt  "+ request)
        val client = OkHttpClient()
        client.newCall(request).enqueue(object: Callback{
            override fun onFailure(call: Call, e: IOException) {
                println("Not yet implemented")
            }

            override fun onResponse(call: Call, response: Response) {
                val body =response?.body?.string()
                println("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjj"+body)

                println("showed toast")


            }
        })


    }



    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}