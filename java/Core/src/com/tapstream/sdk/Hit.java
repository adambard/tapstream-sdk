package com.tapstream.sdk;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

public class Hit {
	public interface CompletionHandler {
		void complete(Response response);
	}

	private String trackerName;
	private String encodedTrackerName;
	private StringBuilder tags = null;

	public Hit(String hitTrackerName) {
		trackerName = hitTrackerName;
		try {
			encodedTrackerName = URLEncoder.encode(hitTrackerName, "UTF-8").replace("+", "%20");
		} catch (UnsupportedEncodingException e) {
			Logging.log(Logging.INFO, "Tapstream Error: Could not encode hit tracker name, exception=%s", e.getMessage());
		}
	}

	public void addTag(String tag) {
		if (tag.length() > 255) {
			Logging.log(Logging.WARN, "Tapstream Warning: Hit tag exceeds 255 characters, it will not be included in the post (tag=%s)", tag);
			return;
		}

		String encodedTag = null;
		try {
			encodedTag = URLEncoder.encode(tag, "UTF-8").replace("+", "%20");
		} catch (UnsupportedEncodingException e) {
			Logging.log(Logging.INFO, "Tapstream Error: Could not encode hit tracker tag %s, exception=%s", tag, e.getMessage());
			return;
		}

		if (tags == null) {
			tags = new StringBuilder("__ts=");
		} else {
			tags.append(",");
		}
		tags.append(encodedTag);
	}

	public String getTrackerName() {
		return trackerName;
	}

	public String getEncodedTrackerName() {
		return encodedTrackerName;
	}

	public String getPostData(boolean debug) {
		if (tags == null) {
			if(debug){
				return "__tsdebug=1";
			}else{
				return "";
			}
		}

		if(debug){
			tags.append("&__tsdebug=1");
		}
		return tags.toString();
	}
}
