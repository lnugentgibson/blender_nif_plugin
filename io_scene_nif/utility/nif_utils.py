import mathutils
import math

class NifExportError(Exception):
    """A simple custom exception class for export errors."""
    pass

def import_matrix(niBlock, relative_to=None):
    """Retrieves a niBlock's transform matrix as a Mathutil.Matrix."""
    # return Matrix(*niBlock.get_transform(relative_to).as_list())
    n_scale, n_rot_mat3, n_loc_vec3 = niBlock.get_transform(relative_to).get_scale_rotation_translation()

    # create a location matrix
    b_loc_vec = mathutils.Vector(n_loc_vec3.as_tuple())
    b_loc_vec = mathutils.Matrix.Translation(b_loc_vec)
    
    # create a scale matrix
    b_scale_mat = mathutils.Matrix.Scale(n_scale, 4)

    # create 3 rotation matrices    
    n_rot_mat = mathutils.Matrix()
    n_rot_mat[0].xyz = n_rot_mat3.m_11, n_rot_mat3.m_12, n_rot_mat3.m_13
    n_rot_mat[1].xyz = n_rot_mat3.m_21, n_rot_mat3.m_22, n_rot_mat3.m_23
    n_rot_mat[2].xyz = n_rot_mat3.m_31, n_rot_mat3.m_32, n_rot_mat3.m_33    
    n_rot_mat = n_rot_mat * b_scale_mat.transposed()
    
    n_euler = n_rot_mat.to_eular()
    b_rot_mat_x = mathutils.Matrix.Rotation(math.radians(-n_euler.x), 4, 'X')
    b_rot_mat_y = mathutils.Matrix.Rotation(math.radians(-n_euler.y), 4, 'Y')
    b_rot_mat_z = mathutils.Matrix.Rotation(math.radians(-n_euler.z), 4, 'Z')
    
    b_rot_mat = b_rot_mat_z * b_rot_mat_y * b_rot_mat_x
    b_rot_mat = b_rot_mat.to_matrix()
    b_import_matrix = b_loc_vec * b_rot_mat * b_scale_mat
    return b_import_matrix


def decompose_srt(self, matrix):
    """Decompose Blender transform matrix as a scale, rotation matrix, and
    translation vector."""
    # get scale components
    # get scale components
    trans_vec, rot_quat, scale_vec = matrix.decompose()
    scale_rot = rot_quat.to_matrix()
    scale_rot_T = mathutils.Matrix(scale_rot)
    scale_rot_T.transpose()
    scale_rot_2 = scale_rot * scale_rot_T
    # and fix their sign
    if (scale_rot.determinant() < 0): scale_vec.negate()
    # only uniform scaling
    # allow rather large error to accomodate some nifs
    if abs(scale_vec[0]-scale_vec[1]) + abs(scale_vec[1]-scale_vec[2]) > 0.02:
        raise NifExportError(
            "Non-uniform scaling not supported."
            " Workaround: apply size and rotation (CTRL-A).")
    b_scale = scale_vec[0]
    # get rotation matrix
    b_rot = scale_rot * b_scale
    # get translation
    b_trans = trans_vec
    # done!
    return [b_scale, b_rot, b_trans]