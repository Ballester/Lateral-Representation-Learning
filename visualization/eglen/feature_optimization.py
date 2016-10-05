def optimize_feature(input_size, x, feature_map):
 config= configOptimization()
 images = np.empty((1,)+input_size)
 img_noise = np.random.uniform(low=0.0, high=1.0, size=input_size)
 config= configOptimization()
 #graph=sess.graph
 #x=graph.get_tensor_by_name("input_image:0")
 sess=tf.get_default_session()
 t_score = tf.reduce_mean(feature_map)
 t_grad = tf.gradients(t_score, x)[0]

 if config.lap_grad_normalization:
  grad_norm=lap_normalize(t_grad[0,:,:,:])
 else:
  grad_norm=normalize_std(t_grad)

 images[0] = img_noise.copy()
 step_size=config.opt_step
 for i in xrange(1,config.opt_n_iters+1):
  feedDict={x: images}
  g, score = sess.run([grad_norm, t_score], feed_dict=feedDict)
  # normalizing the gradient, so the same step size should work for different layers and networks
  images[0] = images[0]+g*step_size
  #l2 decay
  if config.decay:
   images[0] = images[0]*(1-config.decay)
  #gaussian blur
  if config.blur_iter:
   if i%config.blur_iter==0:
    images[0] = gaussian_filter(images[0], sigma=config.blur_width)
  #clip norm
  if config.norm_pct_thrshld:
   norms=np.linalg.norm(images[0], axis=2, keepdims=True)
   n_thrshld=np.sort(norms, axis=None)[int(norms.size*config.norm_pct_thrshld)]
   images[0]=images[0]*(norms>=n_thrshld)
  # #clip contribution
  if config.contrib_pct_thrshld:
   contribs=np.sum(images[0]*g[0], axis=2, keepdims=True)
   c_thrshld=np.sort(contribs, axis=None)[int(contribs.size*config.contrib_pct_thrshld)]
   images[0]=images[0]*(contribs>=c_thrshld)

 return images[0].astype(np.float32)
 
def save_optimazed_image_to_disk(opt_output,channel,n_channels,key,path):
	opt_output_rescaled = (opt_output - opt_output.min())
	opt_output_rescaled *= (255/opt_output_rescaled.max())
	im = Image.fromarray(opt_output_rescaled.astype(np.uint8))
	file_name="opt_"+str(channel).zfill(len(str(n_channels)))+".bmp"
	folder_name=path+"/feature_maps/"+key+"/optimization"
	if not os.path.exists(folder_name):
	  os.makedirs(folder_name)
	im.save(folder_name+"/"+file_name)
