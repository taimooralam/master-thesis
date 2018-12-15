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
		char * fifo = "/tmp/pipe.log";
		mkfifo(fifo, 0777);
		std::cout << " o ";
		fd_fifo = open(fifo, O_WRONLY);
		std::cout << "cc " << std::endl;
		
	}
	
	bool showStatistics;
	pcl::io::compression_Profiles_e compressionProfile;
	pcl::io::OctreePointCloudCompression<pcl::PointXYZ>* PointCloudEncoder;
	pcl::io::OctreePointCloudCompression<pcl::PointXYZ>* PointCloudDecoder;
	int fd_fifo;

	int read_decompressed(std::string filename, pcl::PointCloud<pcl::PointXYZ>::Ptr cloud){
		return pcl::io::loadPCDFile<pcl::PointXYZ>(filename, *cloud);	
	}
	
	int write_compressed(std::stringstream &stream){
		//TODO: write a compressed stringstream to a file

		//send the string stream to the fifo here
		const std::string& tmp = stream.str();
		//std::cout << "last 50 characters of compressed data: \n" << tmp.substr(tmp.length()-50) << std::endl;
		std::cout << " Compressed: " << tmp.length() << std::endl;
		//std::cout << tmp.length() << std::endl;
		std::string encoded = base64_encode(reinterpret_cast<const unsigned char*>(tmp.c_str()), tmp.length()) + "~";
		std::cout << "Encoded: " << encoded.length() << std::endl;  
  		const char* cstr = encoded.c_str();
		write(fd_fifo, cstr, encoded.length()); //todo: correct the arguments here
		
		std::cout << " w ";
		
		return 0;
	}
	
	~Comdecomp(){
		//std::cout << "Destroying Compdecomp: \n";
		delete PointCloudEncoder;
		delete PointCloudDecoder;
		//close the fifo here
		close(fd_fifo);
	}
};



int main(int argc, char ** argv){

	//std::ofstream out("out.txt");
    	//std::streambuf *coutbuf = std::cout.rdbuf(); //save old buf
    	//std::cout.rdbuf(out.rdbuf()); //redirect std::cout to out.txt!
	std::cout << "Start ---- " << std::endl;	
	Comdecomp codec;
	fs::path targetDir(argv[1]);
	fs::directory_iterator it(targetDir), eod;

	BOOST_FOREACH(fs::path const&p, std::make_pair(it, eod)){
		if(fs::is_regular_file(p)){
			pcl::PointCloud<pcl::PointXYZ>::Ptr cloud (new pcl::PointCloud<pcl::PointXYZ>);	

			//if(pcl::io::loadPCDFile<pcl::PointXYZ> ("test_pcd.pcd", *cloud) == -1){
			std::string filename = p.string();
			std::cout << p << std::endl;
			if(codec.read_decompressed(filename, cloud) == -1){
				std::cout << p << std::endl;
				PCL_ERROR("Could read the file  \n");
			}else{
				std::cout << "\n L ";
			}
	
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
	}

	
	//std::cout.rdbuf(coutbuf); //reset to standard output again	
	return 0;
}
