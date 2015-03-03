import unittest
import difflib
from parsing import JavaParser
from repository import *


class TestJavaParser(unittest.TestCase):
    def setUp(self):
        self.code = """
            package org.feup.meoarenacustomer.app;
            import android.app.DownloadManager;

            import com.loopj.android.http.*;


            public class API {
                public String getUrl() {
                    return url;
                }

                public void setUrl(String url) {
                    this.url = url;
                }

                private String url;
                private final String PRODUCTION_URL = "http://neo.andrefreitas.pt:8081/api";
                private static AsyncHttpClient client = new AsyncHttpClient();

                public API(String url ){
                    this.url = url;
                }

                public API(){
                    this.url = PRODUCTION_URL;
                }


                public void login(String email, String password, AsyncHttpResponseHandler responseHandler){
                    RequestParams params = new RequestParams();
                    params.put("email", email);
                    params.put("password", password);
                    client.post(url + "/login", params, responseHandler);
                }

                public void register(String name, String email, String nif, String password, String ccNumber, String ccType, String ccValidity, AsyncHttpResponseHandler responseHandler){
                    RequestParams params = new RequestParams();
                    params.put("name", name);
                    params.put("email", email);
                    params.put("password", password);
                    params.put("nif", nif);
                    params.put("ccNumber", ccNumber);
                    params.put("ccType", ccType);
                    params.put("ccValidity", ccValidity);
                    client.post(url + "/customers", params, responseHandler);
                }

                public void getShows(AsyncHttpResponseHandler responseHandler) {
                    client.get(url + "/shows", responseHandler);
                }

            }"""

    def test_parse(self):
        components = JavaParser.parse(self.code)
        self.assertTrue("API" in components)
        expected_functions = set({"getUrl", "setUrl", "API", "login", "register", "getShows"})
        actual_functions = set(components["API"].functions.keys())
        self.assertEqual(expected_functions, actual_functions)

    def test_extract_method(self):
        method = JavaParser.extract_method("API", "register", self.code)
        expected_method = """register(String name, String email, String nif, String password, String ccNumber, String ccType, String ccValidity, AsyncHttpResponseHandler responseHandler){
                    RequestParams params = new RequestParams();
                    params.put("name", name);
                    params.put("email", email);
                    params.put("password", password);
                    params.put("nif", nif);
                    params.put("ccNumber", ccNumber);
                    params.put("ccType", ccType);
                    params.put("ccValidity", ccValidity);
                    client.post(url + "/customers", params, responseHandler);
                }"""
        ratio = difflib.SequenceMatcher(None, expected_method, method).ratio()
        self.assertTrue(ratio == 1.0)

    def test_diff(self):
        code_b = """
            package org.feup.meoarenacustomer.app;
            import android.app.DownloadManager;

            import com.loopj.android.http.*;


            public class API {
                public String getUrl() {
                    return url;
                }

                public void setUrl(String url) {
                    this.url = url;
                }

                private String url;
                private final String PRODUCTION_URL = "http://neo.andrefreitas.pt:8081/api";
                private static AsyncHttpClient client = new AsyncHttpClient();

                public API(String url ){
                    this.url = url;
                }

                public API(){
                    this.url = PRODUCTION_URL;
                }

                // Modified method
                public void login(String email, String password, AsyncHttpResponseHandler responseHandler){
                    RequestParams params = new RequestParams();
                    params.put("email", email);
                    client.post(url + "/login", params, responseHandler);
                }

                // New method
                public void recover(String name){
                    RequestParams params = new RequestParams();
                    params.put("name", name);
                    params.put("email", email);
                }

                // Renamed method
                public void outputShows(AsyncHttpResponseHandler responseHandler) {
                    client.get(url + "/shows", responseHandler);
                }

                public void getShows(AsyncHttpResponseHandler responseHandler) {
                    client.get(url + "/shows", responseHandler);
                }

            }"""
        diffs = JavaParser.diff(("API.java", self.code), ("API.java", code_b))

        # Detect if a method has been added
        filter_diff = [diff for diff in diffs if isinstance(diff, DiffMethod) and diff.method_b == "recover" and diff.added == True]
        self.assertTrue(len(filter_diff) > 0)

        # Detect unmodified methods
        filter_diff = [diff for diff in diffs if isinstance(diff, DiffMethod) and diff.method_a == "getShows"]
        self.assertTrue(len(filter_diff) == 0)

        # Detect removed methods
        filter_diff = [diff for diff in diffs if isinstance(diff, DiffMethod) and diff.method_a == "register" and diff.removed == True]
        self.assertTrue(len(filter_diff) > 0)

        # Detect modified methods
        filter_diff = [diff for diff in diffs if isinstance(diff, DiffMethod) and diff.method_a == "login" and diff.modified == True]
        self.assertTrue(len(filter_diff) > 0)

        # Detect modified classes
        filter_diff = [diff for diff in diffs if isinstance(diff, DiffClass) and diff.class_a == "API" and diff.modified == True]
        self.assertTrue(len(filter_diff) > 0)


if __name__ == '__main__':
    unittest.main()