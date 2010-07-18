import numpy as np
import dipy as dp
import nibabel as ni
import resources
import time

#Registration options
#similarity 'cc', 'cr', 'crl1', 'mi', je', 'ce', 'nmi', 'smi'.  'cr'
similarity='cr'
#interp 'pv', 'tri'
interp =  'tri'
#subsampling None or sequence (3,)
subsampling=None
#search 'affine', 'rigid', 'similarity' or ['rigid','affine']
search='affine'
#optimizer 'simplex', 'powell', 'steepest', 'cg', 'bfgs' or
#sequence of optimizers
optimizer= 'powell'


def eddy_current_correction(data,affine):
    result=[]
    
    no_dirs=data.shape[-1]
    for i in range(1,no_dirs):        
        target=ni.Nifti1Image(data[:,:,:,0],affine)
        source=ni.Nifti1Image(data[:,:,:,i],affine)        
        T=dp.volume_register(source,target,similarity,\
                                 interp,subsampling,search,optimizer)
        sourceT=dp.volume_transform(source, T.inv(), reference=target)
        print i, sourceT.get_data().shape, sourceT.get_affine().shape
        result.append(sourceT)

    result.insert(0,target)
    print 'no of images',len(result)
    return ni.concat_images(result)

def register_source_2_target(source_data,source_affine,target_data,target_affine):

    #subsampling=target_data.shape[:3]

    target=ni.Nifti1Image(target_data,target_affine)
    source=ni.Nifti1Image(source_data,source_affine)
    T=dp.volume_register(source,target,similarity,\
                              interp,subsampling,search,optimizer)
    sourceT=dp.volume_transform(source, T.inv(), reference=target)

    return sourceT

def save_volumes_as_mosaic(fname,volume_list):

    import Image
    
    vols=[]
    for vol in volume_list:
    
        sh=vol.shape    
        arr=vol.reshape(sh[0],sh[1]*sh[2])
        arr=arr.astype('ubyte')

        print 'arr.shape',arr.shape
        
        vols.append(arr)

    mosaic=np.concatenate(vols)    

    Image.fromarray(mosaic).save(fname)


if __name__ == '__main__':

    #dicom directories
    dname_grid_101=resources.get_paths('DSI STEAM 101 Trio')[2]
    dname_shell_114=resources.get_paths('DTI STEAM 114 Trio')[2]

    data_101,affine_101,bvals_101,gradients_101=dp.load_dcm_dir(dname_grid_101)    
    data_114,affine_114,bvals_114,gradients_114=dp.load_dcm_dir(dname_shell_114)

    print data_101.shape,data_114.shape
    
    '''
    t1=time.clock()
    res=eddy_current_correction(data,affine)
    t2=time.clock()
    print 'final shape',res.get_data().shape
    '''

    img_101T=register_source_2_target(data_101[...,0],affine_101,data_114[...,0],affine_114)
    save_volumes_as_mosaic('/tmp/mosaic1.png',[img_101T.get_data(),data_114[...,0]])
    


    
