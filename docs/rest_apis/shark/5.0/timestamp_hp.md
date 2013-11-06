High precision timestamp value.

Since REST API clients may have very different needs and capabilitities when it comes to handling high-precision timestamps, the API supports multiple encodings for timestamps with higher precision than a seconds.

The format of a high-precision timestamp value in a request or response object is defined by three attributes:
&lt;units&gt;.&lt;precision&gt; &lt;type&gt;

* units: s, ms, us, ns
* precision: .ms, .us, .ns *(optional)*
* type: string, number *(only relevant for JSON)*

Here are a few examples:

<table class="paramtable">
<tr><th>Format</th><th>Value</th><th>XML</th><th>JSON</th></tr>
<tr><td>s string</td><td>1336086278.462862235</td><td>1336086278</td><td>"1336086278"</td></tr>
<tr><td>s number</td><td>1336086278.462862235</td><td>1336086278</td><td>1336086278</td></tr>
<tr><td>s.ns string</td><td>1336086278.462862235</td><td>1336086278.462862235</td><td>"1336086278.462862235"</td></tr>
<tr><td>s.ns number</td><td>1336086278.462862235</td><td>1336086278.462862235</td><td>1336086278.462862235</td></tr>
<tr><td>s.ms string</td><td>1336086278.462862235</td><td>1336086278.462</td><td>"1336086278.462"</td></tr>
<tr><td>ns string</td><td>1336086278.462862235</td><td>1336086278462862235</td><td>"1336086278462862235"</td></tr>
<tr><td>ns number</td><td>1336086278.462862235</td><td>1336086278462862235</td><td>1336086278462862235</td></tr>
</table>

<p></p>

To select a specific timestamp format to be used in the request and response body for any REST API call, the client must indicate the desired format in the <code>X-RBT-High-Precision-Timestamp-Format</code> HTTP Header. The same value applies to both the request and response structures.

For example, to select nanosecond units formatted as a string (for JSON), the header would be specified as <code>X-RBT-High-Precision-Timestamp-Format: ns string</code>.

If the header is not supplied by the client, the default encoding is <code>ns number</code>.

> _The selection of the type "string" versus "number" is only relevant for JSON (since in XML everything is a string), and the choice depends on the client's particular characteristics. For example, JavaScript can only represent a 53-bit integer value before losing precision. That corresponds to roughly microsecond resolution, so it is not possible to store "ns number" values in a JavaScript integer with full precision, hence a a JavaScript client that requires sub-microsecond precision must use a string encoding and parse the number manually. However, since Python has no such constraints, the easiest encoding to work with would be a nanosecond number._
