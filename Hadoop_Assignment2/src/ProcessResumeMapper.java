
import java.io.IOException;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.json.JSONException;
import org.json.JSONObject;

public class ProcessResumeMapper
  extends Mapper<Text, Text, Text, Text> {

  
  @Override
  public void map(Text key, Text value, Context context)
      throws IOException, InterruptedException {
	 
	String line = value.toString(); 	
	//System.out.println("Yes1");

    String[] parts = line.split("\n");
	//Dictionary dict = new Hashtable();
    JSONObject obj = new JSONObject();

   int flag=0;


//    Map<String, String> objects = new HashMap<String, String>();
  //  System.out.println("Yes2");
   String filePathString = context.getInputSplit().toString();
    //String filePathString="Anil";

    for(int i=0;i<parts.length;i++)
    {
    	//System.out.println("Yes3");
    	String[] parts1 = parts[i].split(":");
	//	System.out.println("YES4:"+parts1.length);
//
    	
    		if(parts1[0].equals("Project1".replaceAll(" ","").toLowerCase()))
    		{	flag=1;
    		
    		}
    		else if(parts1[0].equals("Project2".replaceAll(" ","").toLowerCase()))
    		{
    			flag=2;
    		}
    	
    	if(parts1.length>=2){
    		//System.out.println("Yes5");
    		//System.out.println(parts1);
    		String type  = (parts1[0].replaceAll(" ","")).toLowerCase();
    		String values= parts1[1];
    		//System.out.println("Yes6");
    		//dict.put(type, values);
    		 try {
    			 if(flag==1)
    			 {
    				 obj.put("1"+type, values);
    			 }
    			 else if(flag==2)
    			 {
    					obj.put("2"+type, values);

    			 }
    			 else
    			 {
 					obj.put(type, values);

    			 }
			} catch (JSONException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
    		 if(parts1[0]=="End Date".replaceAll(" ","").toLowerCase());
    		 {
    			 flag=0;
    		 }
    	}
    }
    String req= obj.toString();;
    context.write(new Text(filePathString),new Text(req));
    }
}


