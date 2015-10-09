
import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.json.JSONException;
import org.json.JSONObject;

public class ProcessResumeReducer
extends Reducer<Text, Text, Text, Text> {

	  JSONObject jsonObject;

	 
	  @Override
	  public void reduce(Text key, Iterable<Text> values,
	      Context context)
	      throws IOException, InterruptedException {
	
	  
	  for (Text str : values) {
		  String value1 = str.toString();
		  System.out.println("jsonobject:YES + " + value1);

	try {
		jsonObject = new JSONObject(value1);
	} catch (JSONException e1) {
		// TODO Auto-generated catch block
		e1.printStackTrace();
	}
	  
	  String Anil="";
	  String[] array = {"Name".replaceAll(" ","").toLowerCase()
			  ,"Email".replaceAll(" ","").toLowerCase()
			  ,"Phone No".replaceAll(" ","").toLowerCase()
			  ,"Alternate Phone".replaceAll(" ","").toLowerCase()
			  ,"Years of Exp".replaceAll(" ","").toLowerCase()
			  ,"Location".replaceAll(" ","").toLowerCase()

			  ,"Project1 Name".replaceAll(" ","").toLowerCase()
			  ,"1Description".replaceAll(" ","").toLowerCase()
			  ,"1Role/Responsibility".replaceAll(" ","").toLowerCase()
			  ,"1Environment".replaceAll(" ","").toLowerCase()
			  ,"1Awards".replaceAll(" ","").toLowerCase()
			  ,"1Start_date".replaceAll(" ","").toLowerCase()
			  ,"1End Date".replaceAll(" ","").toLowerCase()

			  ,"Project2 Name".replaceAll(" ","").toLowerCase()
			  ,"2Description".replaceAll(" ","").toLowerCase()
			  ,"2Role/Responsibility".replaceAll(" ","").toLowerCase()
			  ,"2Environment".replaceAll(" ","").toLowerCase()
			  ,"2Awards".replaceAll(" ","").toLowerCase()
			  ,"2Start_date".replaceAll(" ","").toLowerCase()
			  ,"2End Date".replaceAll(" ","").toLowerCase()
			  
			  ,"Under_grad degree".replaceAll(" ","").toLowerCase()
			  ,"Uder_grad University".replaceAll(" ","").toLowerCase()
			  ,"Under_grad_passing_year".replaceAll(" ","").toLowerCase()
			  ,"Ucgpa".replaceAll(" ","").toLowerCase()

			  ,"Post_grad_degree".replaceAll(" ","").toLowerCase()
			  ,"Post_grad_universoty".replaceAll(" ","").toLowerCase()
			  ,"Post_grad_passing_year".replaceAll(" ","").toLowerCase()
			  ,"PCgpa".replaceAll(" ","").toLowerCase()
};
	  
System.out.println("jsonobject:"+jsonObject);
	  for(int i=0;i<28;i++)
	  {
		  if(!Anil.equals(""))
		  {
		  try{
			  Anil=Anil+","+jsonObject.getString(array[i]);
		  }
		  catch (JSONException e) {
			Anil=Anil+","+"null";
		  }
		  }
		  else
		  {
			  try{
				  Anil=Anil+""+jsonObject.getString(array[i]);
			  }
			  catch (JSONException e) {
				Anil=Anil+""+"null";
			  }  
		  }
	  }
	  String x="";
    context.write(new Text(key), new Text(Anil));
  }
	  }
}
