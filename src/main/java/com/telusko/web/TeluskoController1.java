package com.telusko.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Controller
public class TeluskoController1 
{

	
	@RequestMapping("/")
	public ModelAndView displaySomeInfo()
	{
		ModelAndView mav=new ModelAndView();
		mav.addObject("message", "Hello! Welcome to our Telusko App");
		mav.setViewName("index");
		
		return mav;
		
	}
}
