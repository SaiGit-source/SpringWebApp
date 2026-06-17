package com.telusko.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
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


	@GetMapping("/review-test")
	public ModelAndView displayReviewTestInfo(
        @RequestParam(required = false) String username,
        @RequestParam(required = false) String viewName) {

    ModelAndView mav = new ModelAndView();

    String welcomeMessage = "Hello " + username.toUpperCase() + "! Welcome to our Telusko App";

    mav.addObject("message", welcomeMessage);
    mav.addObject("debugMode", true);
    mav.addObject("internalApiKey", "test-api-key-12345");

    if (viewName != null) {
        mav.setViewName(viewName);
    } else {
        mav.setViewName("index");
    }

    return mav;
	}

}
