
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

/**
 * The driver class to execute our document extraction MapReduce job. Implements
 * ToolRunner to allow the use of command line variables. Requires two inputs
 * the input folder containing our binary documents and the output folder to
 * store the extracted delimited file.
 */
public class ProcessResume extends Configured implements Tool
{

	public static void main(String[] args) throws Exception
	{
		int exit = ToolRunner.run(new Configuration(), new ProcessResume(), args);
		System.exit(exit);
	}

	@Override
	public int run(String[] args) throws Exception
	{
		Configuration conf = new Configuration();
		// setting the input split size 64lMB or 128MB are good.
		//conf.setInt("mapreduce.input.fileinputformat.split.maxsize", 67108864);
		Job job = new Job(conf, "ProcessResume");
		// now we optionally set the delimiter and replacement character
		//conf.setStrings("com.ibm.imte.tika.delimiter", "\n");
		//conf.setStrings("com.ibm.imte.tika.replaceCharacterWith", " ");
		job.setJarByClass(ProcessResume.class);
		job.setJobName("ProcessResume");
		
		FileSystem fs = FileSystem.get(new Configuration());
	    fs.delete(new Path(args[1]), true);


		// Finally we have to set our input and output format classes
		job.setInputFormatClass(MyFileFormat.class);
		//job.setOutputFormatClass(TikaOutputFormat.class);

		FileInputFormat.addInputPath(job, new Path(args[0]));

		job.setMapperClass(ProcessResumeMapper.class);
	    job.setReducerClass(ProcessResumeReducer.class);
		
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(Text.class);

		FileOutputFormat.setOutputPath(job, new Path(args[1]));
		return job.waitForCompletion(true) ? 0 : 1;
	}
}