#include <iostream>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl/io/tar.h>
#include <boost/any.hpp>
#include <boost/filesystem.hpp>
#include <boost/foreach.hpp>
#include <pcl/compression/octree_pointcloud_compression.h>
#include <sstream>
#include <typeinfo>
#include "base64.h"
#include <fcntl.h>
#include <boost/lexical_cast.hpp>
namespace fs = boost::filesystem;


class Comdecomp
{
public:

	Comdecomp(){
		//constructor
	
		showStatistics = false;
		compressionProfile = pcl::io::MED_RES_ONLINE_COMPRESSION_WITHOUT_COLOR;
		PointCloudEncoder = new pcl::io::OctreePointCloudCompression<pcl::PointXYZ>(compressionProfile, showStatistics);
		PointCloudDecoder = new pcl::io::OctreePointCloudCompression<pcl::PointXYZ>();
		//Open the fifo here
		char * fifo_length = "/tmp/pipe_length.log";
		char * fifo_data = "/tmp/pipe_data.log";
		//mkfifo(fifo, 0777);
		std::cout << " o ";
		fd_fifo_length = open(fifo_length, O_RDONLY);
		fd_fifo_data = open(fifo_data, O_RDONLY);
		int pipe_sz = fcntl(fd_fifo_data, F_SETPIPE_SZ, 16777216);
		std::cout << "cc Size of pipes set:" << pipe_sz << "Result: " <<  getpagesize()  <<  std::endl;
		
	}
	
	bool showStatistics;
	pcl::io::compression_Profiles_e compressionProfile;
	pcl::io::OctreePointCloudCompression<pcl::PointXYZ>* PointCloudEncoder;
	pcl::io::OctreePointCloudCompression<pcl::PointXYZ>* PointCloudDecoder;
	int fd_fifo_length;
	int fd_fifo_data;

	std::string read_compressed(){
		//uint32_t len;
		//read(fd_fifo_length, &len, sizeof(len));
		std::vector<char> buf_len(32+1);
		read(fd_fifo_length, buf_len.data(), 32);
		buf_len[32] = '\0';
		int length;
		std::istringstream ss(buf_len.data());
		ss >> length;
		

		char * char_ptr = new char[length];
		char_ptr[length-1] = '\0';
		read(fd_fifo_data, char_ptr, length);
		std::string return_data(char_ptr);
		delete char_ptr;
		return return_data.substr(0, return_data.size()-1);	
	}
	
	int write_decompressed(pcl::PointCloud<pcl::PointXYZ>::Ptr cloudOut, std::string filename){
		pcl::io::savePCDFileBinaryCompressed(filename, *cloudOut);
  		std::cerr << "Saved  data points to" << filename << std::endl;	
		return 0;
	}
	
	~Comdecomp(){
		std::cout << "Destroying Compdecomp: \n";
		delete PointCloudEncoder;
		delete PointCloudDecoder;
		//close the fifo here
		close(fd_fifo_length);
		close(fd_fifo_data);
	}
};



int main(int argc, char ** argv){

	std::cout << "Start ---- " << std::endl;	
	Comdecomp codec;
	int i = 1;
	while (i< 60){
		std::string compressed = codec.read_compressed();
		std::cout << "Encoded: " << compressed.length();
		std::string decoded = base64_decode(compressed);
		std::cout << " Compressed: " << decoded.length();
		std::stringstream ss;
		ss.str(decoded);
	
		pcl::PointCloud<pcl::PointXYZ>::Ptr cloudOut(new pcl::PointCloud<pcl::PointXYZ> ());


      		// decompress point cloud
      		codec.PointCloudDecoder->decodePointCloud(ss, cloudOut);

		std::cout << "dc ";

		codec.write_decompressed(cloudOut, "data/" + boost::lexical_cast<std::string>(i)+".pcd");
		std::cout << "w " << std::endl;
		i++;
	}	


	/*BOOST_FOREACH(fs::path const&p, std::make_pair(it, eod)){
		if(fs::is_regular_file(p)){
			//std::cout << p << std::endl;
			pcl::PointCloud<pcl::PointXYZ>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZ>);	

			//if(pcl::io::loadPCDFile<pcl::PointXYZ> ("test_pcd.pcd", *cloud) == -1){
			std::string filename = p.string();
			if(codec.read_decompressed(filename, cloud) == -1){
				PCL_ERROR("Could read the file  \n");
			}else{
				std::cout << "\n L 
	
			std::stringstream compressed_data;
			codec.PointCloudEncoder->encodePointCloud(cloud, compressed_data);
			codec.write_compressed(compressed_data);
			//std::cout << compressed_data.str().size() << std::endl;
			//std::cout << typeid(compressed_data).name() << std::endl;
			//std::cout << "Loaded "
				//<< cloud->width * cloud->height
				//<< " data points from test_pcd.pcd with the following fields: " << std::endl;
		}else{
			std::cout << "Not a regular file" << std::endl;
		}
	}*/

	
	//std::cout.rdbuf(coutbuf); //reset to standard output again	
	return 0;
}
