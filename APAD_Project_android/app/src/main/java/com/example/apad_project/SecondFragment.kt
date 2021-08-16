package com.example.apad_project

import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
// import androidx.navigation.fragment.navArgs
import com.example.apad_project.databinding.FragmentSecondBinding

/**
 * A simple [Fragment] subclass as the second destination in the navigation.
 */
class SecondFragment : Fragment() {

    private var _binding: FragmentSecondBinding? = null

    // This property is only valid between onCreateView and
    // onDestroyView.
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        _binding = FragmentSecondBinding.inflate(inflater, container, false)
        return binding.root

    }
    val args: SecondFragmentArgs by navArgs()
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.buttonLogout.setOnClickListener {
            findNavController().navigate(R.id.action_SecondFragment_to_FirstFragment)
        }

        val email = args.myArg
        println("the parameterrrrrrr "+email)

        view.findViewById<Button>(R.id.button_createpost).setOnClickListener {
            val action = SecondFragmentDirections.actionSecondFragmentToCreatePosts2(email)

            findNavController().navigate(action)

            //findNavController().navigate(R.id.action_SecondFragment_to_create_posts2)
        }
        view.findViewById<Button>(R.id.button_viewpost).setOnClickListener {
            //val action1 = SecondFragmentDirections.actionSecondFragmentToViewPosts(email)
            findNavController().navigate(R.id.action_SecondFragment_to_view_post)
            //findNavController().navigate(R.id.action_SecondFragment_to_view_Posts)
        }

    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}